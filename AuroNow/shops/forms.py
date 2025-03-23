# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import ShopOwner

class ShopOwnerSignUpForm(UserCreationForm):
    name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=True)
    shop_name = forms.CharField(max_length=255, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, required=True)
    
    class Meta:
        model = ShopOwner
        fields = ('name', 'email', 'password1', 'password2', 'phone', 'shop_name', 'address', 'latitude', 'longitude')
