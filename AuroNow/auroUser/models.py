from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from shops.models import ShopOwner, Service

# Custom Manager for Users
class CustomerManager(BaseUserManager):
    def create_user(self, email, name, password=None, phone=None):
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

# Customer Model
class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    objects = CustomerManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

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
    
    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

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
