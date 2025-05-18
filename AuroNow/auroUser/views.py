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


# Importing environment variables
env = environ.Env()
environ.Env.read_env()
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)


# Helper function to get random shops data
def get_shop_data(limit=5):
    shops = ShopOwner.objects.all()[:limit]
    shops_data = []

    for shop in shops:
        # Get all images related to the shop
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [image.shop_image.url for image in shop_images if image.shop_image]

        # Get all service categories ()
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

        # Get customer reviews and rating
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()

        # Calculate the average rating
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        shops_data.append({
            'id': shop.id,
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,  # Display the number of reviews
            'rating': avg_rating_of_shop,  # Display the average rating
        })

    return shops_data

# View for base layout showing recommended shops
def base_layout(request):
    # categories = ServiceCategory.objects.values_list('name', flat=True).distinct()

    # print("category:", categories)

    context = {
        'shops': get_shop_data(),
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    }
    return render(request, 'base_layout.html', context)

# Search Results View
def search_results(request):
    # Capture query parameters
    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip(),
        'address': request.GET.get('address', '').strip(),
        'price_range': request.GET.get('price', '').strip(),
    }


    # Start with all shops
    shops = ShopOwner.objects.all()

    # Filter by shop name if provided
    if query['shop_name']:
        shops = shops.filter(shop_name__icontains=query['shop_name'])

    # Filter by address if provided
    if query['address']:
        shops = shops.filter(address__icontains=query['address'])

    # Filter by category if provided
    if query['category']:
        shops = shops.filter(categories__name__iexact=query['category'])
    

    # Now filter by price
    filtered_shops = []

    for shop in shops.distinct():
            #get  services
        services = Service.objects.filter(shop=shop).all()

        # Apply price range filter if selected
        if query['price_range']:
            try:
                if query['price_range'].endswith('+'):
                    min_price = float(query['price_range'][:-1])
                    services = services.filter(price__gte=min_price)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    services = services.filter(price__gte=min_p, price__lte=max_p)
            except ValueError:
                print("Invalid price range format provided:", query['price_range'])

        # Only add the shop if it has services matching the price filter
        if services.exists():
            filtered_shops.append(shop)
       
    # Build final results
    results = []

    for shop in filtered_shops:
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [img.shop_image.url for img in shop_images if img.shop_image]
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()
        
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()

        # Calculate the average rating
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        results.append({
            'id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,  # Display the number of reviews
            'rating': avg_rating_of_shop,  # Display the average rating
        })


    # Render the search results page
    return render(request, 'search_results.html', {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    })


def shop_detail(request, id):
    # Fetch the shop with optimized queries
    shop = get_object_or_404(
        ShopOwner.objects.prefetch_related(
            'services',
            'staff',
            'timings',
            'images',
        ),
        id=id
    )

    # Get all shop images
    shop_images = shop.images.all()
    image_urls = [ img.shop_image.url for img in shop_images if img.shop_image ]
    #get categories = 
    # Get categories related to this shop
    categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

    # Get services with categories
    services = shop.services.all().select_related('category')
    
    # Get active staff members
    staff_members = shop.staff.filter(is_active=True)
   
    # Get shop timings ordered by day
    shop_timings = shop.timings.all().order_by('day')
    
    # Get ratings and reviews with user information
    customer_rating_list = RatingAndReviews.objects.filter(
        shop=shop
    ).select_related(
        'user'  # Optimize user queries
    ).order_by('-id')  # Newest first
    
    customer_rating_count = customer_rating_list.count()
    
    # Calculate average rating
    avg_rating = customer_rating_list.aggregate(Avg('rating'))
    avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0
    context = {
        'id':shop.id,
        'shop': shop,
        'images': image_urls,
        'reviews': customer_rating_count,
        'rating': avg_rating_of_shop,
        'customer_rating_list': customer_rating_list[:5],  # Only show 5 most recent
        'now': timezone.now(),
        'services': services,
        'staff_members': staff_members,
        'timings': shop_timings,
        'categories': categories if categories else ["General"],
    }
    
    return render(request, 'shop_detail.html', context)



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

        isUserExist = User.objects.get(email=email)

        if isUserExist:
            messages.error(request, 'The user already exist.')
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
        
        return render(request, 'resetPass.html')
    except UserPasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid token')
        return redirect('user_login')
# ------------------------------Reset Password End-----------------------------------------------
