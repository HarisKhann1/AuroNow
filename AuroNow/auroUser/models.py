from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from shops.models import ShopOwner, Service, Staff
import uuid
import datetime

# Custom Manager for Users
class CustomerManager(BaseUserManager):
    def create_user(self, email, name, password=None, phone=None, city=None,  **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            city=city,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, phone = "03161111111", city = "karachi", password=None, **extra_fields):
        # Set admin privileges for superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(
            email=email,
            name=name,
            password=password,
            phone=phone,
            city=city,
            **extra_fields
        )



# Customer Model
class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=255, default="Karachi")

    # Admin-related fields - default to False for regular users
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # False by default - no admin access
    is_superuser = models.BooleanField(default=False)  # False by default - no admin privileges
    
    objects = CustomerManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # Django admin compatibility
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
# user forget password
class UserPasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        # Token valid for 24 hours
        return (datetime.datetime.now().timestamp() - self.created_at.timestamp()) < 86400
    
# Book Appointments
class BookAppointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments")
    
    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    def __str__(self):
        return f"Appointment by {self.user.name} at {self.shop.name} on {self.appointment_date}"

# Ratings & Reviews
class RatingAndReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField()

# Queries from Users
class Queries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="queries")
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE, related_name="queries")
    question = models.TextField()
    response = models.TextField(null=True, blank=True)
