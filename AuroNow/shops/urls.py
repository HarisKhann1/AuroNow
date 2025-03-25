from django.urls import path
from shops import views

urlpatterns = [
    path('signup/', views.dashboard_signup_view, name='dashboard_signup'),
    path('login/', views.dashboard_login_view, name='dashboard_login'),
    path('', views.dashboard_home, name='dashboard_home'),
]
