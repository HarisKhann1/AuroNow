from django.urls import path
from shops import views

urlpatterns = [
    path('signup/', views.dashboard_signup_view, name='dashboard_signup'),
    path('login/', views.dashboard_login_view, name='dashboard_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('', views.dashboard_home, name='dashboard_home'),
]
