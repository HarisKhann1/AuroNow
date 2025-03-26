from django.urls import path
from shops import views
import uuid

urlpatterns = [
    # auth routes
    path('signup/', views.dashboard_signup_view, name='dashboard_signup'),
    path('login/', views.dashboard_login_view, name='dashboard_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
    # dshboard routes
    path('', views.dashboard_home, name='dashboard_home'),
    path('te/', views.temp, name='dashboard_products'),
]
