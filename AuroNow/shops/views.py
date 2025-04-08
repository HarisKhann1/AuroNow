from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import ShopOwnerSignUpForm
from .models import ShopOwner, ServiceCategory, Service, ShopImage, Staff, FAQ
from .models import PasswordResetToken
from django.conf import settings
import environ
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError

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

    # get categories for pagination
    categories = ServiceCategory.objects.filter(shop=user).order_by('name').reverse()
    pagination = Paginator(categories, 5)  # Show 5 categories per page 
    
    # get services for pagination
    services = Service.objects.filter(shop=user).order_by('name').reverse()
    service_pagination = Paginator(services, 5)  # Show 5 services per page

    # search for categories and services
    if request.method == 'GET':
            # search and pagination for categories
            search_term = request.GET.get('categorySearch')
            if search_term:
                services = ServiceCategory.objects.filter(shop=user, name__icontains=search_term).order_by('name').reverse()
                pagination = Paginator(services, 5)

            page_number = request.GET.get('table-page', 1)  # Default to page 1 if not provided
            page_obj = pagination.get_page(page_number) #this variable hold data according to the page number
            total_page = page_obj.paginator.num_pages
            
            # search and pagination for services
            service_search_term = request.GET.get('serviceSearch')
            if service_search_term:
                services = Service.objects.filter(shop=user, name__icontains=service_search_term).order_by('name').reverse()
                service_pagination = Paginator(services, 5)
            
            service_page_number = request.GET.get('service-page', 1)  # Default to page 1 if not provided
            service_page_obj = service_pagination.get_page(service_page_number)
            service_total_page = service_page_obj.paginator.num_pages

    # get all categories for the service select option form
    total_categories = ServiceCategory.objects.filter(shop=user)

    services_count = Service.objects.filter(shop=user).count()
    categories_count = ServiceCategory.objects.filter(shop=user).count()
    context = {
        'page_obj': page_obj, # Categories pagination object
        'totalPageList': [i+1 for i in range(total_page)], # Create a list of page numbers for categories data
        'total_categories': total_categories, # Total categories for service select option form
        'service_page_obj': service_page_obj, # Services pagination object
        'service_totalPageList': [i+1 for i in range(service_total_page)], # Create a list of page numbers for services data
        'services_count': services_count, # Total services count
        'categories_count': categories_count, # Total categories count
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

# edit service category view
def edit_category_view(request, id):
    if request.method == 'POST':
        user = request.user
        category_name = request.POST.get('categoryName')
        category_instance = ServiceCategory.objects.get(shop=user, id=int(id))
        category_instance.name = category_name
        category_instance.save()
        return redirect('dashboard_service')
    return redirect('dashboard_service')  # Redirect to services page

# delete service category view
def delete_category_view(request, id):
    if request.method == 'POST':
        user = request.user
        category_instance = ServiceCategory.objects.get(shop=user, id=int(id))
        category_instance.delete()
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

def edit_service_view(request, id):
    if request.method == 'POST':
        user = request.user
        service_name = request.POST.get('service-name')
        service_category = request.POST.get('service-category')
        service_price = request.POST.get('service-price')
        service_duration = request.POST.get('service-duration')
        service_description = request.POST.get('service-description')

        if service_name and service_category and service_price and service_duration and service_description:
            category_instance = ServiceCategory.objects.get(shop=user, id=int(service_category))
            Service.objects.filter(shop=user, id=int(id)).update(
                category=category_instance,
                name=service_name,
                price=float(service_price),
                description=service_description,
                duration=int(service_duration)
            )
            return redirect('dashboard_service')
    return redirect('dashboard_service')  # Redirect to services page

def delete_service_view(request, id):
    if request.method == 'POST':
        user = request.user
        service_instance = Service.objects.get(shop=user, id=int(id))
        service_instance.delete()
        return redirect('dashboard_service')
    return redirect('dashboard_service')  # Redirect to services page

# -------------- add service page end --------------------------------------

# -------------- add shop images start --------------------------------------
# add shop images view
@login_required(login_url='dashboard_login')
def dashboard_images_upload_view(request):
    user = request.user
    MAX_ALLOWED_IMAGES = 3
    
    # Get current image count
    images_count = ShopImage.objects.filter(shop=user).count()
    shop_images = ShopImage.objects.filter(shop=user)
        
    if request.method == 'POST':
        images = request.FILES.getlist('shop-images')

        # Check if total would exceed limit
        if images_count + len(images) > MAX_ALLOWED_IMAGES:
            messages.error(request, f'Maximum {MAX_ALLOWED_IMAGES} images allowed. You already have {images_count}.')
            return redirect('dashboard_upload_images')
        else:
            # Create image objects
            for image in images:
                ShopImage.objects.create(shop=user, shop_image=image)
            messages.success(request, 'Images uploaded successfully!')
            return redirect('dashboard_upload_images')
    context = {
        'shop_images': shop_images, # All images of the shop
    }
    return render(request, 'dashboard/addShopImages.html', context)

def delete_shop_image_view(request, id):
    if request.method == 'POST':
        user = request.user
        image_instance = ShopImage.objects.get(shop=user, id=int(id))
        image_instance.delete()
        return redirect('dashboard_upload_images')
    return redirect('dashboard_upload_images')  # Redirect to images upload page

def edit_shop_image_view(request, id):
    if request.method == 'POST':
        user = request.user
        image_instance = ShopImage.objects.get(shop=user, id=int(id))
        new_image = request.FILES.get('shop-image')
        if new_image:
            image_instance.shop_image = new_image
            image_instance.save()
            return redirect('dashboard_upload_images')
    return redirect('dashboard_upload_images')  # Redirect to images upload page
# -------------- add shop images end --------------------------------------

# -------------- dashboard add staff start --------------------------------------
def dashboard_add_staff_view(request):
    user = request.user
    staff_list = Staff.objects.filter(shop=user).order_by('id').reverse()
    staff_count = Staff.objects.filter(shop=user).count()

    # search and pagination
    pagination = Paginator(staff_list, 5)  # Show 5 categories per page 

    # search for staff, with pagination
    if request.method == 'GET':
            search_term = request.GET.get('staffSearch')
            if search_term:
                staff_list = Staff.objects.filter(shop=user, name__icontains=search_term).order_by('name').reverse()
                pagination = Paginator(staff_list, 5)

            page_number = request.GET.get('staff-table-page', 1)  # Default to page 1 if not provided
            page_obj = pagination.get_page(page_number) #this variable hold data according to the page number
            total_page = page_obj.paginator.num_pages

    # add staff
    if request.method == 'POST':
        staff_name = request.POST.get('staff-name')
        staff_phone = request.POST.get('staff-phone-no')
        staff_role = request.POST.get('staff-role')
        try:
            if staff_name and staff_phone and staff_role:
                Staff.objects.create(phone=staff_phone, shop=user, name=staff_name, role=staff_role).save()
                messages.success(request, 'Staff added successfully!')
                return redirect('dashboard_staff')
        except IntegrityError:
            messages.error(request, 'A staff member with this information already exists')
            return redirect('dashboard_staff')
        
    context = {
        'staff_count': staff_count,
        'page_obj': page_obj, #this variable hold data according to the page number
        'totalPageList': [i+1 for i in range(total_page)], # Create a list of page numbers for categories data
    }
    return render(request, 'dashboard/addStaff.html', context)

def dashboard_edit_staff_view(request, id):
    user = request.user

    if request.method == 'POST':
        staff_name = request.POST.get('staff-name')
        staff_phone = request.POST.get('staff-phone-no')
        staff_role = request.POST.get('staff-role')
        
        try:
            if staff_name and staff_phone and staff_role:
                staff_instance = Staff.objects.get(shop=user, id=int(id))
                staff_instance.phone = staff_phone
                staff_instance.shop = user
                staff_instance.name = staff_name
                staff_instance.role = staff_role
                staff_instance.save()
                return redirect('dashboard_staff')
        except IntegrityError:
            messages.error(request, 'A staff member with this information already exists')
            return redirect('dashboard_staff')
    else:
        return redirect('dashboard_staff')
    
def dashboard_delete_staff_view(request, id):
    user = request.user

    if request.method == 'POST':
        staff_instance = Staff.objects.get(shop=user, id=int(id))
        staff_instance.delete()
        return redirect('dashboard_staff')
    return redirect('dashboard_staff')

# -------------- dashboard add staff end --------------------------------------

# -------------- dashboard add FAQs --------------------------------------
def dashboard_faqs_view(request):
    user = request.user
    faqs = FAQ.objects.filter(shop=user).order_by('id').reverse()
    faqs_count = FAQ.objects.filter(shop=user).count()

    # search and pagination
    pagination = Paginator(faqs, 5)  # Show 5 categories per page 

    # search for faqs, with pagination
    if request.method == 'GET':
            search_term = request.GET.get('faqSearch')
            if search_term:
                faqs = FAQ.objects.filter(shop=user, question__icontains=search_term).order_by('question').reverse()
                pagination = Paginator(faqs, 5)

            page_number = request.GET.get('faq-table-page', 5)  # Default to page 5 if not provided
            page_obj = pagination.get_page(page_number) #this variable hold data according to the page number
            total_page = page_obj.paginator.num_pages

    # add faq
    if request.method == 'POST':
        faq_question = request.POST.get('faq-question')
        faq_answer = request.POST.get('faq-answer')
        try:
            if faq_question and faq_answer:
                FAQ.objects.create(shop=user, question=faq_question, answer=faq_answer).save()
                messages.success(request, 'FAQ added successfully!')
                return redirect('dashboard_faq')
        except IntegrityError:
            messages.error(request, 'FAQ cannot be added')
            return redirect('dashboard_faq')
    
    context = {
        'faqs_count': faqs_count,
        'page_obj': page_obj, #this variable hold data according to the page number
        'totalPageList': [i+1 for i in range(total_page)], # Create a list of page numbers for categories data
    }
    return render(request, 'dashboard/addFAQs.html', context)

# dashboard edit faq view
def dashboard_edit_faq_view(request, id):
    user = request.user

    if request.method == 'POST':
        faq_question = request.POST.get('faq-question')
        faq_answer = request.POST.get('faq-answer')
        
        try:
            if faq_question and faq_answer:
                faq_instance = FAQ.objects.get(shop=user, id=int(id))
                faq_instance.question = faq_question
                faq_instance.answer = faq_answer
                faq_instance.save()
                return redirect('dashboard_faq')
        except Exception:
            messages.error(request, 'FAQ cannot be updated, something went wrong!')
            return redirect('dashboard_faq')
    else:
        return redirect('dashboard_faq')
    
# dashboard delete faq view
def dashboard_delete_faq_view(request, id):
    user = request.user

    if request.method == 'POST':
        faq_instance = FAQ.objects.get(shop=user, id=int(id))
        faq_instance.delete()
        return redirect('dashboard_faq')
    return redirect('dashboard_faq')
