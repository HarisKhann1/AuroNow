from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import datetime
import uuid

'''
This module defines the models for the shop owners and their services in the AuroNow application.
It includes the ShopOwner model, which is the custom user model for shop owners, and other related models such as ServiceCategory, Service, Staff, Slot, FAQ, Advertisement, and ShopImage.
These models are used to manage shop owners, their services, staff members, appointment slots, FAQs, advertisements, and shop images.
note: shop attribute each model store shop id
'''

# Custom Manager for Shop Owners
class ShopOwnerManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Shop owners must have an email address')
        
        shop_owner = self.model(
            email=self.normalize_email(email),
            name=name,
            **extra_fields
        )
        
        shop_owner.set_password(password)
        shop_owner.save(using=self._db)
        return shop_owner
    
    def create_superuser(self, email, name, shop_name, password=None, **extra_fields):
        # Set admin privileges for superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(
            email=email,
            name=name,
            shop_name=shop_name,
            password=password,
            **extra_fields
        )

# Shop Owner Model
class ShopOwner(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    shop_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Admin-related fields - default to False for regular salon owners
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # False by default - no admin access
    is_superuser = models.BooleanField(default=False)  # False by default - no admin privileges
    
    objects = ShopOwnerManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'shop_name']
    
    def __str__(self):
        return f"{self.shop_name} ({self.email})"
class PasswordResetToken(models.Model):
    user = models.ForeignKey(ShopOwner, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        # Token valid for 24 hours
        return (datetime.datetime.now().timestamp() - self.created_at.timestamp()) < 86400


# Service Categories
class ServiceCategory(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# Services
class Service(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default='')
    duration = models.IntegerField(help_text="Duration in minutes")

# Staff Members
class Staff(models.Model):
    phone = models.CharField(max_length=20)
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='staff')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)

    class Meta:
        unique_together = ('phone', 'shop')

# Appointment Slots
class Slot(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

# FAQs for Shops
class FAQ(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE,related_name='faqs')
    question = models.TextField()
    answer = models.TextField()

# Advertisements
class Advertisement(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='advertisements')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

# Shop Images
class ShopImage(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='images')
    shop_image = models.ImageField(upload_to='shop_images/', blank=True, null=True)

class ShopTiming(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='timings')
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    # is_open = models.BooleanField(default=True)  # Open/Close status
    is_closed = models.BooleanField(default=False)  # Sunday off etc.

    class Meta:
        unique_together = ('shop', 'day')  # Avoid duplicate day entries

    def __str__(self):
        return f"{self.shop.name} - {self.get_day_display()}"
