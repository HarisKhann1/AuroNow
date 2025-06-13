from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from auroUser.models import  RatingAndReviews, User, UserPasswordResetToken
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from shops.models import ShopOwner, ServiceCategory, ShopImage,Service
from django.core.mail import send_mail
import environ
from django.conf import settings
import h3
from geopy.distance import geodesic

 
# Importing environment variables
env = environ.Env()
environ.Env.read_env()
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)


# Helper function to get random shops data
def get_shop_data(limit=5):
    shops = ShopOwner.objects.all()[:limit]
    shops_data = []

    for shop in shops:
        # Fetch related shop images
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [image.shop_image.url for image in shop_images if image.shop_image]

        # Fetch distinct service categories
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

        # Fetch reviews and calculate average rating
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        # Append to shop data list
        shops_data.append({
            'id': shop.id,
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,
            'rating': avg_rating_of_shop,
        })

    return shops_data

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
        print("user:", user)
        if user is not None:
            print("in if condition of user login")
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
        name = request.POST.get('name')
        email = request.POST.get('email')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        print(email, city, phone, password)
        # isUserExist = User.objects.get(email=email)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'The user already exists.')
            return render(request, 'auth/signup.html')

        # Create a new user
        User.objects.create_user(
            name=name,
            email=email,
            phone=phone,
            city=city,
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
