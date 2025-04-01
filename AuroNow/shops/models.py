from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import datetime
import uuid
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

# Shop Owner Model
class ShopOwner(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    shop_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
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
    shop_email = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
