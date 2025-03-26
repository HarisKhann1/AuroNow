from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import ShopOwnerSignUpForm
from .models import ShopOwner
from .models import PasswordResetToken
from django.conf import settings
import environ

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
        try:
            shop_owner = ShopOwner.objects.get(email=email)
            if shop_owner.check_password(password):
                login(request, shop_owner)
                return redirect('dashboard_home')
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('dashboard_login')  # Redirect back to login page
        except ShopOwner.DoesNotExist:
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
            
            reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{token.token}"
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

def dashboard_home(request):
    try:
        return render(request, 'base_dashboard.html')
    except TemplateDoesNotExist:
        return HttpResponse("Page not found", status=404)
