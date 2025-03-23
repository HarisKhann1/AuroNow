from django.urls import path
from shops import views

urlpatterns = [
    path('signup/', views.dashboard_signup_view, name='dashboard_signup'),
    path('', views.dashboard_home, name='dashboard_home'),
]
