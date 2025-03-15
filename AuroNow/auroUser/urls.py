from django.urls import path
from auroUser import views

urlpatterns = [
    path('', views.home, name='home'),
]
