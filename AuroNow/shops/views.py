from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import ShopOwnerSignUpForm
from .models import ShopOwner

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
        except ShopOwner.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')   

def dashboard_home(request):
    try:
        return render(request, 'base_dashboard.html')
    except TemplateDoesNotExist:
        return HttpResponse("Page not found", status=404)
