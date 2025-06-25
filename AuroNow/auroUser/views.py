from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from auroUser.models import  RatingAndReviews, User, UserPasswordResetToken, BookAppointment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from shops.models import ShopOwner, ServiceCategory, ShopImage,Service, Staff
from django.core.mail import send_mail
import environ
from django.conf import settings
import h3
from geopy.distance import geodesic
from requests import get
from auroUser.recommended_shop import get_top_rated_shops_by_city

 
# Importing environment variables
env = environ.Env()
environ.Env.read_env()
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)


# Helper function to get random shops data
def get_shop_data():
    recommanded_shops = get_top_rated_shops_by_city('karachi', limit=8)
    
    return recommanded_shops

# ----------------------------
# View: Base Layout with Filters and Recommended Shops
# ----------------------------
def base_layout(request):
   
    results = {
        'shops': get_shop_data(),
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    }
    return render(request, 'base_layout.html', results)



# ----------------------------
# H3 Geolocation Helpers
# ----------------------------

def latlng_to_cell(lat, lon, resolution=9):
    return h3.latlng_to_cell(lat, lon, resolution)

def nearby_shops(request):
    # Get user coordinates
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        print("DEBUG: Location not provided.")
        return render(request, 'nearby_shops.html', {'error': 'Location not provided.'})

    lat, lon = float(lat), float(lon)
    user_coords = (lat, lon)
    print(f"DEBUG: User coordinates: {user_coords}")

    # Extract query filters
    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip(),
        'city': request.GET.get('city', '').strip(),
        'price_range': request.GET.get('price', '').strip(),
    }
    print(f"DEBUG: Query filters: {query}")

    # Get H3 hex rings (2km ~= k_ring 3)
    resolution = 9
    center_hex = h3.latlng_to_cell(lat, lon, resolution)
    nearby_hexes = h3.grid_disk(center_hex, 3)
    print(f"DEBUG: Center hex: {center_hex}, Nearby hexes: {len(nearby_hexes)}")

    all_shops = ShopOwner.objects.filter(latitude__isnull=False, longitude__isnull=False)
    print(f"DEBUG: Total shops with coordinates: {all_shops.count()}")

    # First: filter by proximity (2km max)
    nearby_shops = []
    for shop in all_shops:
        shop_coords = (shop.latitude, shop.longitude)
        distance_km = geodesic(user_coords, shop_coords).km
        print(f"DEBUG: Shop '{shop.shop_name}' is {distance_km:.2f} km away.")

        if distance_km <= 2:
            nearby_shops.append((shop, distance_km))

    print(f"DEBUG: Shops within 2km: {len(nearby_shops)}")

    # Apply additional filters
    filtered_shops = nearby_shops


    # Filter: category
    if query['category']:
        shop_ids = [s.id for s, _ in filtered_shops]
        category_shop_ids = Service.objects.filter(
            shop_id__in=shop_ids,
            category__name__iexact=query['category']
        ).values_list('shop_id', flat=True).distinct()

        filtered_shops = [(s, d) for (s, d) in filtered_shops if s.id in category_shop_ids]
        print(f"DEBUG: After category filter: {len(filtered_shops)}")

    # Filter: price
    final_shops = []
    for shop, distance_km in filtered_shops:
        services = Service.objects.filter(shop=shop)

        if query['price_range']:
            try:
                if query['price_range'].endswith('+'):
                    min_price = float(query['price_range'][:-1])
                    services = services.filter(price__gte=min_price)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    services = services.filter(price__gte=min_p, price__lte=max_p)
            except ValueError:
                print("DEBUG: Invalid price format received.")
                services = Service.objects.filter(shop=shop)  # fallback to all services

        if services.exists():
            final_shops.append((shop, distance_km))
        else:
            print(f"DEBUG: Shop {shop.shop_name} excluded due to no services.")

    print(f"DEBUG: Final shops after price filtering: {len(final_shops)}")
    final_shops.sort(key=lambda x: x[1])

    # Build results for template
    results = []
    for shop, distance_km in final_shops:
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [img.shop_image.url for img in shop_images if img.shop_image]

        categories = ServiceCategory.objects.filter(
            services__shop=shop
        ).values_list('name', flat=True).distinct()

        reviews = RatingAndReviews.objects.filter(shop=shop)
        review_count = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))
        avg_rating_value = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] else 0

        results.append({
            'id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': review_count,
            'rating': avg_rating_value,
            'distance': round(distance_km, 2),  # distance in km, rounded for display
        })

    print(f"DEBUG: Total results sent to template: {len(results)}")

    return render(request, 'nearby_shops.html', {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
        'is_near_shops': True,
})
# ----------------------------
# View: Search Results with Filters and Nearby H3 Radius
# ----------------------------
def search_results(request):

    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip(),
        'city': request.GET.get('city', '').strip(),
        'price_range': request.GET.get('price', '').strip(),
    }
 
    shops = ShopOwner.objects.all()

    # Apply filters
    if query['shop_name']:
        print("Filtering by name:", query['shop_name'])
        shops = shops.filter(shop_name__icontains=query['shop_name'])
    if query['city']:
        print("Filtering by city:", query['city'])
        shops = shops.filter(city__icontains=query['city'])
    if query['category']:
        category_shop_ids = Service.objects.filter(
            shop__in=shops,
            category__name__iexact=query['category']
        ).values_list('shop_id', flat=True).distinct()
        shops = shops.filter(id__in=category_shop_ids)

    filtered_shops = []
    for shop in shops.distinct():
        services = Service.objects.filter(shop=shop)

        if query['price_range']:
            try:
                if query['price_range'].endswith('+'):
                    min_price = float(query['price_range'][:-1])
                    services = services.filter(price__gte=min_price)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    services = services.filter(price__gte=min_p, price__lte=max_p)
                print(f"Price filter applied for shop {shop.id}")
            except ValueError:
                print("Invalid price range:", query['price_range'])

        if services.exists():
            filtered_shops.append(shop)


    # Build results context
    results = []
    for shop in filtered_shops:
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [img.shop_image.url for img in shop_images if img.shop_image]
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        results.append({
            'id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,
            'rating': avg_rating_of_shop,
        })

    return render(request, 'search_results.html', {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    })

# ----------------------------
# View: Shop Detail Page
# ----------------------------
def shop_detail(request, shop_id):
    # Fetch shop with related data to avoid multiple DB hits
    shop = get_object_or_404(
        ShopOwner.objects.prefetch_related(
            'services', 'staff', 'timings', 'images',
        ),
        id=shop_id
    )

    # Get shop images
    shop_images = shop.images.all()
    image_urls = [img.shop_image.url for img in shop_images if img.shop_image]

    # Get categories
    categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

    # Get services and staff
    services = shop.services.all().select_related('category')
    staff_members = shop.staff.filter(is_active=True)

    # Get shop timings ordered by day
    WEEKDAY_ORDER = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    shop_timings = sorted(
        shop.timings.all(),
        key=lambda x: WEEKDAY_ORDER.index(x.day))

    # Get latest 5 reviews with user info
    customer_rating_list = RatingAndReviews.objects.filter(shop=shop).select_related('user').order_by('-id')
    customer_rating_count = customer_rating_list.count()
    avg_rating = customer_rating_list.aggregate(Avg('rating'))
    avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

    
    # Prepare context
    results = {
        'shop_id': shop.id,
        'shop': shop,
        'images': image_urls,
        'reviews': customer_rating_count,
        'rating': avg_rating_of_shop,
        'customer_rating_list': customer_rating_list[:5],
        'now': timezone.now(),
        'services': services,
        'staff_members': staff_members,
        'shop_timings': shop_timings,
        'categories': categories if categories else ["General"],
        "longitude" : shop.longitude,
        "latitude" : shop.latitude,
    }
    
    return render(request, 'shop_detail.html', results)


# ------------------------------Login view Start---------------------------------------------
# User login View
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)  # use email here
        if user is not None:
            login(request, user)
            return redirect('base_layout')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'auth/login.html')
# ------------------------------Login view End-----------------------------------------------

# ------------------------------Logout View Start-----------------------------------------------
# User Logout View
def logout_view(request):
    logout(request)
    # Redirect to the base layout after logout
    return redirect('base_layout')
# ------------------------------Logout View End-------------------------------------------------

# ------------------------------Signup View Start-------------------------------------------------
# User Singup View
def user_signup(request):

    if request.method == 'POST':
        loc = get('http://ip-api.com/json/')
        city = loc.json().get('city', 'N/A')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # isUserExist = User.objects.get(email=email)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'The user already exists.')
            return render(request, 'auth/signup.html')

        # Create a new user
        User.objects.create_user(
            name=name,
            email=email,
            phone=phone,
            city=city.lower(),
            password=password
        ).save()
        # Log the user in after registration
        user = authenticate(request, email=email, password=password)  # use email here
        if user is not None:
            login(request, user)
            # Redirect to the base layout after login
            return redirect('base_layout')  
        else:
            messages.error(request, 'Registration successful but login failed. Please try again.')
            return render(request, 'auth/signup.html')
        
    return render(request, 'auth/signup.html')
# ------------------------------Signup View End---------------------------------------------------

# ------------------------------Forget Password Start---------------------------------------------
def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        if user:
            # Generate a password reset token and send it to the user's email
            token = UserPasswordResetToken.objects.create(user=user)
            # Send email logic
            reset_link = f"{request.scheme}://{request.get_host()}/user/reset-password/{token.token}"
            send_mail(
                'Password Reset', # Subject of the email
                f'Click the link to reset your password: {reset_link}', # Body of the email
                EMAIL_HOST_USER, # Sender's email
                [email], # Recipient's email
                fail_silently=False, # Set to True in production
            )
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('user_login')  # Redirect to login page after sending email
        else:
            messages.error(request, 'Email not found.')

    return render(request, 'auth/forget_password.html')
# ------------------------------Forget Password End-----------------------------------------------

# ------------------------------Reset Password Start---------------------------------------------
def user_reset_password(request, token):
    try:
        token_obj = UserPasswordResetToken.objects.get(token=token)
        
        if not token_obj.is_valid():
            messages.error(request, 'Token expired')
            return redirect('user_login')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
            else:
                user = token_obj.user
                user.set_password(password)
                user.save()
                token_obj.delete()
                messages.success(request, 'Password reset successful')
                return redirect('user_login')
        
        return render(request, 'auth/reset_password.html')
    except UserPasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid token')
        return redirect('user_login')
# ------------------------------Reset Password End-----------------------------------------------

# ------------------------------Booking System--------------------------------------------------

def service_cart_details(request=None):
    user_selected_service_details = request.session.get('user_selected_service_details', [])
    
    return user_selected_service_details
    # # calculate the total price and duration of the selected services
    # total_duration = 0
    # total_price = 0.0
    
    # for service in user_selected_service_details:
    #     total_price += service['price']
    #     total_duration += service['duration']
    
    # # transform the total duration from minutes to hours and minutes
    # total_hours = total_duration // 60 # integer division to get hours
    # total_minutes = total_duration % 60 # modulus to get remaining minutes

    # return user_selected_service_details

    
def bookingSystem(request, shop_id=None):
    # get the shop and service dettails from the shoping cart
    user_selected_service_details = service_cart_details(request)
    shop_name = ShopOwner.objects.filter(id=shop_id).first().shop_name if shop_id else None
    # ------------------------------------------------------------------------------------
    # calculate the total price and duration of the selected services
    total_duration = 0
    total_price = 0.0
    print("DEBUG: User selected service details:", user_selected_service_details)
    print("type of user_selected_service_details:", type(user_selected_service_details))
    print("length of user_selected_service_details:", len(user_selected_service_details) if user_selected_service_details else 0)
    length = len(user_selected_service_details) if user_selected_service_details else 0
    if length > 0:
        for service in user_selected_service_details:
            total_price += service['price']
            total_duration += service['duration']
    
    # transform the total duration from minutes to hours and minutes
    total_hours = total_duration // 60 # integer division to get hours
    total_minutes = total_duration % 60 # modulus to get remaining minutes

    # ------------------------------------------------------------------------------------
    # get the shop services details
    services_list = []
    if shop_id:
        services = Service.objects.filter(shop=shop_id)
        if services:
            for service in services:
                services_list.append({
                    'id': service.id,
                    'name': service.name,
                    'price': float(service.price),
                    'duration': service.duration,
                    'shop': service.shop.id,
                    'image': service.service_image.url if service.service_image else None,
                })
    
    context = {
        'shop_name': shop_name,
        'user_selected_service_details': user_selected_service_details if user_selected_service_details else [],
        'shop_services': services_list,
        'shop_id': shop_id,
        'total_price': total_price,
        'total_duration': total_duration,
        'service_count': len(user_selected_service_details),
        'total_hours': total_hours,
        'total_minutes': total_minutes,
    }
    return render(request, 'select_services.html', context)

# ------------------------------Booking System End ---------------------------------------------

# ------------------------------ add Service to Cart Start ---------------------------------------------
def add_service_to_cart(request, shop_id, service_id):
    # Initialize the session cart if it doesn't exist
    if 'user_selected_service_details' not in request.session:
        request.session['user_selected_service_details'] = []

    # Copy the cart from session
    user_selected_service_details = request.session['user_selected_service_details']

    # make sure the session only collect the one shop services if not then clear the session
    if user_selected_service_details and user_selected_service_details[0]['shop'] != shop_id:
        user_selected_service_details = []
        request.session['user_selected_service_details'] = user_selected_service_details

    # Fetch the service to be added
    service = Service.objects.filter(shop=shop_id, id=service_id).first()

    if service:
        service_data = {
            'id': service.id,
            'name': service.name,
            'price': float(service.price),
            'duration': service.duration,
            'shop': service.shop.id,
        }

        # Avoid duplicates by checking service ID
        if not any(s['id'] == service.id for s in user_selected_service_details):
            user_selected_service_details.append(service_data)
            request.session['user_selected_service_details'] = user_selected_service_details
            request.session.modified = True  # Ensure session is saved

    return redirect('shopping-cart', shop_id)  # Redirect to booking page
# ------------------------------ add Service to Cart End ---------------------------------------------

# ------------------------------ Remove Service from Cart Start ---------------------------------------------
# Remove a service from the cart
def remove_service_from_cart(request, shop_id ,service_id):
    user_selected_service_details = request.session.get('user_selected_service_details', [])
    
    # Filter out the service to be removed
    user_selected_service_details = [
        service for service in user_selected_service_details if service['id'] != service_id
    ]
    
    # Update the session
    request.session['user_selected_service_details'] = user_selected_service_details
    request.session.modified = True  # Ensure session is saved

    return redirect('shopping-cart', shop_id)  # Redirect to booking page

# ------------------------------ Remove Service from Cart End ---------------------------------------------

# ------------------------------ Mobile Screen services Cart ---------------------------------------------
def mobile_remove_servies_cart(request):
     # get the shop and service dettails from the shoping cart
    user_selected_service_details = service_cart_details(request)
    # ------------------------------------------------------------------------------------
    # calculate the total price and duration of the selected services
    total_duration = 0
    total_price = 0.0

    length = len(user_selected_service_details) if user_selected_service_details else 0
    if length > 0:
        for service in user_selected_service_details:
            total_price += service['price']
            total_duration += service['duration']
    
    # transform the total duration from minutes to hours and minutes
    total_hours = total_duration // 60 # integer division to get hours
    total_minutes = total_duration % 60 # modulus to get remaining minutes

    context = {
        'user_selected_service_details': user_selected_service_details if user_selected_service_details else [],
        'total_price': total_price,
        'total_duration': total_duration,
        'service_count': length,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
    }

    return render(request, 'delete_mobile_shop_Services.html', context)
# ------------------------------ Mobile Screen services Cart Start ---------------------------------------------
# ------------------------------ Choice of Staff Start ----------------------------------------------
def choose_staff(request):
    staff_members = []
    service_cart_list = service_cart_details(request);
    # ------------------------------------------------------------------------------------
    # calculate the total price and duration of the selected services
    total_duration = 0
    total_price = 0.0
    
    for service in service_cart_list:
        total_price += service['price']
        total_duration += service['duration']
    
    # transform the total duration from minutes to hours and minutes
    total_hours = total_duration // 60 # integer division to get hours
    total_minutes = total_duration % 60 # modulus to get remaining minutes

    # ------------------------------------------------------------------------------------
    print("DEBUG: Service cart list:", service_cart_list)
    if len(service_cart_list) == 0:
        return redirect('base_layout')
    
    # Get the shop ID and fetch the staff members
    shop_id = service_cart_list[0]['shop']
    shop_staff = Staff.objects.filter(shop_id=shop_id, is_active=True).order_by('name')
    if shop_staff.exists():
        for staff in shop_staff:
            staff_members.append({
                'id': staff.id,
                'name': staff.name,
            })

    # from auroUser.calculate_slote import find_available_slots
    # shop_id = 2
    # requested_services = [
    #     {'staff_id': 4, 'duration': 40},
    #     {'staff_id': 2, 'duration': 20}
    # ]
    # available_slots = find_available_slots(shop_id, requested_services)
    # print('slotes',available_slots)

    context = {
        'shop_id': shop_id,
        'staff_members': staff_members,
        'service_cart_list': service_cart_list,
        'total_price': total_price,
        'total_duration': total_duration,
        'service_count': len(service_cart_list),
        'total_hours': total_hours,
        'total_minutes': total_minutes,
    }

    return render(request, 'choose_professional.html', context)

# ------------------------------ Choice of Staff End ----------------------------------------------

# ------------------------------ select date and time for booking Start ---------------------------

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
@csrf_exempt  # ONLY for testing. Use CSRF token in production!
def select_date_and_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print("DEBUG: Received JSON data:", data)
            
            # user selected appointment date
            appointment_date = data[-1]['date']
            request.session['appointment_date'] = appointment_date
            
            """
            staff_service_dic = {}
            count = 1
            if data:
                for service in data:
                    if count == len(data):
                        break
                    count += 1
                    staff_service_dic[int(service['selectedProfessional'])] = int(service['duration'])
            print("DEBUG: Staff service dictionary:", staff_service_dic)
            """

            staff_service_tuple = []
            count = 1
            if data:
                for service in data:
                    if count == len(data):
                        break
                    count += 1
                    staff_service_tuple.append((int(service['selectedProfessional']), int(service['duration'])))
            print("DEBUG: Staff service tuple:", staff_service_tuple)
            # ----------------------------------------------------------------------------------------------
            from auroUser.calculate_slote import get_available_slots
            user_selected_service_details = request.session.get('user_selected_service_details', [])
            # Get available slots
            shop_id = user_selected_service_details[0]['shop'] if user_selected_service_details else None
            print("DEBUG: Shop ID:", shop_id)
            # appointment_date = "2025-6-10"

            common_slots, individual_slots = get_available_slots(
                shop_id, staff_service_tuple, appointment_date
            )

            print("DEBUG: Individual staff slots:", individual_slots)
            staff_ids = []
            for staff_id, slots in individual_slots.items():
                staff_ids.append(staff_id)
            request.session['staff_ids'] = staff_ids
            print("DEBUG: Staff IDs:", staff_ids)

            from auroUser.common_slotes import find_common_continuous_slots
            result = find_common_continuous_slots(individual_slots)
            # add the above common slotes result to the django session
            request.session['common_slots'] = result
            print("DEBUG: Resulting continuous slots:", result)
        # ----------------------------------------------------------------------------------------------

            return HttpResponse('{"status": "success", "message": "Data received successfully!"}', content_type='application/json')
        
        except Exception as error:
            print("DEBUG: Error parsing JSON data:", error)
            return HttpResponse('{"status": "error", "message": "Invalid data format"}', content_type='application/json', status=400)

    return HttpResponse('{"status": "error", "message": "Invalid request method"}', content_type='application/json', status=405)
# ------------------------------ select date and time for booking End -----------------------------
@login_required(login_url='user_login')
def select_slot(Request):
    # get the appointment date from the session
    appointment_date = Request.session.get('appointment_date', None)
    user_selected_service_details = Request.session.get('user_selected_service_details', [])

    # get the common slots from the session
    common_slots = Request.session.get('common_slots', [])

    context = {
        'common_slots': common_slots,
        'today': appointment_date,
        'user_selected_service_details': user_selected_service_details,
    }
    return render(Request, 'select_appointment_date.html', context)
# ------------------------------ select date and time for booking End -----------------------------

# ------------------------------ Booking Confirmation Start ---------------------------------------------
@login_required(login_url='user_login')
def booking_confirmed(request):
    # get the user_selected_service_details from the session
    user_selected_service_details = request.session.get('user_selected_service_details', [])
    staff_ids = request.session.get('staff_ids', [])

    # get the duration from the session
    durations = []
    for service in user_selected_service_details:
        durations.append(service['duration'])
    print("DEBUG: duation:", durations)


    if request.method == 'POST':
        selectedSlot = request.POST.get('selectedSlot')
        customer_id = request.POST.get('customerId')

        print("DEBUG: customerid", customer_id)
        print("DEBUG: Selected slot:", selectedSlot)
        from auroUser.exact_slotes import split_time_slots
        slots = split_time_slots(selectedSlot, durations)
        print(slots)  # [('09:00', '10:00'), ('10:00', '10:45')]
        print("DEBUG: user_selected_service_details:", user_selected_service_details)

        merged_all_service_appointments_data = []
        for i,service in enumerate(user_selected_service_details):
            service_data = {
                'user_id': customer_id,
                'shop_id': service['shop'],
                'service_id': service['id'],
                'staff_id': staff_ids[i] if i < len(staff_ids) else None,  # Ensure we don't go out of bounds
                'appointment_date': request.session.get('appointment_date', None),
                'start_time': slots[i][0] if i < len(slots) else None,  # Ensure we don't go out of bounds
                'end_time': slots[i][1] if i < len(slots) else None,  # Ensure we don't go out of bounds
            }
            merged_all_service_appointments_data.append(service_data)
            print("DEBUG: Merged appointment data:", merged_all_service_appointments_data)

        # Create the appointment in the database
        from auroUser.models import BookAppointment
        for appointment_data in merged_all_service_appointments_data:
            appointment = BookAppointment.objects.create(
                user_id=appointment_data['user_id'],
                shop_id=appointment_data['shop_id'],
                service_id=appointment_data['service_id'],
                staff_id=appointment_data['staff_id'],
                appointment_date=appointment_data['appointment_date'],
                start_time=appointment_data['start_time'],
                end_time=appointment_data['end_time'],
            )
            appointment.save()
            print("DEBUG: Appointment created:", appointment)
        
    # Clear the session data after booking
    request.session['user_selected_service_details'] = []
    request.session['appointment_date'] = None
    request.session['common_slots'] = []
    request.session['staff_ids'] = []
    print("DEBUG: Session data cleared after booking.")
    messages.success(request, 'Booking confirmed successfully!')
    return redirect('base_layout')  # Redirect to the base layout after booking confirmation
# ------------------------------ Booking Confirmation End ---------------------------------------------

# ---------------------------- Customer Appointment History View Start ---------------------------------------------
@login_required(login_url='user_login')
def customer_appointment_history(request):
    user = request.user
    # recent top 20 appointments for the user
    appointments = list(BookAppointment.objects.filter(user_id=user.id).select_related('shop', 'service', 'staff').order_by('-appointment_date', '-start_time', '-end_time')[:20])
    # appointments.reverse()

    appointment_list = []
    for appointment in appointments:
        appointment_list.append({
            'id': appointment.id,
            'shop_name': appointment.shop.shop_name,
            'service_name': appointment.service.name,
            'staff_name': appointment.staff.name if appointment.staff else "N/A",
            'appointment_date': appointment.appointment_date,
            'start_time': appointment.start_time,
            'end_time': appointment.end_time,
            'status': appointment.status,
        })

    context = {
        'appointments': appointment_list,
        'user': user,
    }

    return render(request, 'user_appointment.html', context)
# ----------------------------- Customer Appointment History View End ---------------------------------------------

# ---------------------------- User Profile View Start ---------------------------------------------
@login_required(login_url='user_login')
def user_profile(request):
    user = request.user
    user_details = User.objects.filter(id=user.id).first()
    
    name = user_details.name if user_details else "N/A"
    email = user_details.email if user_details else "N/A"
    phone = user_details.phone if user_details else "N/A"
    city = user_details.city if user_details else "N/A"


    context = {
        'user': user,
        'name': name,
        'email': email,
        'phone': phone,
        'city': city,
    }
    return render(request, 'user_profile.html', context)
# ---------------------------- User Profile View End ---------------------------------------------

# --------------------------- Update User Profile -------------------------------------
@login_required(login_url='user_login')
def update_user_profile(request):
    loc = get('http://ip-api.com/json/')
    city = loc.json().get('city', 'N/A')
    
    user = request.user
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Update user details
        user.name = name
        user.email = email
        user.phone = phone
        user.city = city.lower()  
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')
# --------------------------- Update User Profile End -------------------------------------

# --------------------------- Update User Password -------------------------------------
@login_required(login_url='user_login')
def change_user_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')

        user = request.user

        # Set the new password
        user.set_password(password)
        user.save()

        messages.success(request, 'Password changed successfully!')
        return redirect('edit_profile')
    

# --------------------------- User review and rating start -------------------------------------

def review(request, shop_id):
    if request.method == 'POST':
        user_id = request.user
        user_rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        
        shop_instance = ShopOwner.objects.get(id=shop_id)
        response = RatingAndReviews.objects.create(
            user = user_id,
            shop = shop_instance,
            rating = user_rating,
            review = review_text
        )

        print(response)
        if (response):
            messages.success(request, 'Thank You for your feedback!')
      
        return redirect('shop_detail', shop_id)


# --------------------------- User review and rating end ---------------------------------------