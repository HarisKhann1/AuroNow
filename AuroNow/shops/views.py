from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import ShopOwnerSignUpForm
from .models import ShopOwner, ServiceCategory, Service
from .models import PasswordResetToken
from django.conf import settings
import environ
from django.contrib.auth.decorators import login_required

# -------------- authentication start --------------------------------------
def dashboard_signup_view(request):
    if request.method == 'POST':
        form = ShopOwnerSignUpForm(request.POST)
        if form.is_valid():
            shop_owner = form.save()
            shop_owner.set_password(form.cleaned_data.get('password1'))
            login(request, shop_owner)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard_home')  # Redirect to dashboard
    else:
        form = ShopOwnerSignUpForm()
   
    return render(request, 'signup.html', {'form': form})

def dashboard_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Use the authenticate method to check the credentials
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')  # Redirect after successful login
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('dashboard_login')  # Redirect back to login page
    return render(request, 'login.html')

def forgot_password(request):
    env = environ.Env()
    environ.Env.read_env()
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')

    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = ShopOwner.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)
            
            reset_link = f"{request.scheme}://{request.get_host()}/dashboard/reset-password/{token.token}"
            send_mail(
                'Password Reset',
                f'Click the link to reset your password: {reset_link}',
                EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link sent to your email')
            return redirect('dashboard_login')
        except ShopOwner.DoesNotExist:
            messages.error(request, 'Email not found')
    
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        
        if not token_obj.is_valid():
            messages.error(request, 'Token expired')
            return redirect('dashboard_login')
        
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
                return redirect('dashboard_login')
        
        return render(request, 'resetPass.html')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid token')
        return redirect('dashboard_login')
# -------------- authentication end --------------------------------------

# -------------- dashboard start --------------------------------------
# dahboard home view
@login_required(login_url='dashboard_login')
def dashboard_home(request):
    try:
        return render(request, 'base_dashboard.html')
    except TemplateDoesNotExist:
        return HttpResponse("Page not found", status=404)
    
# -------------- add service page start --------------------------------------
# services page view
def dashboard_service_view(request):
    user = request.user
   
    categories = ServiceCategory.objects.filter(shop=user)
    context = {
        'categories': categories,
    }
    return render(request, 'dashboard/services.html', context)

# add service category view
def add_service_category_view(request):

    if request.method == 'POST':
        user = request.user
        service_category = request.POST.get('category')
        if service_category:
            ServiceCategory.objects.create(name=service_category, shop=user).save()
            return redirect('dashboard_service')
    return redirect('dashboard_service')  # Redirect to services page

# add service view
def add_service_view(request):
    if request.method == 'POST':
        user = request.user
        service_name = request.POST.get('service-name')
        service_category = request.POST.get('service-category')
        service_price = request.POST.get('service-price')
        service_duration = request.POST.get('service-duration')
        service_description = request.POST.get('service-description')

        if service_name and service_category and service_price and service_duration and service_description:
            category_instance = ServiceCategory.objects.get(shop=user, id=int(service_category))
            print(service_category, 'I am hit');
            Service.objects.create(
                shop=user,
                category=category_instance,
                name=service_name,
                price=float(service_price),
                description=service_description,
                duration=int(service_duration)
            ).save()
            return redirect('dashboard_service')
    return redirect('dashboard_service')  # Redirect to services page

# -------------- add service page end --------------------------------------
