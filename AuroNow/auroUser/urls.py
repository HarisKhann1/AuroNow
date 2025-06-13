from django.urls import path
from . import views



urlpatterns = [
    # authentication urls
    path('login/', views.user_login, name='user_login'),  # URL for user registration
    path('logout/', views.logout_view, name='user_logout'),  # URL for user logout
    path('signup/', views.user_signup, name='user_signup'),  # URL for user login
    path('forget-password/', views.forget_password, name='user_forget_password'),  # URL for password reset
    path('user/reset-password/<uuid:token>/', views.user_reset_password, name='user_reset_password'),
    
    # main urls
    path('', views.base_layout, name='base_layout'),  # URL for the base_layout
    path('search-results/', views.search_results, name='search_results'), 
    path('shop/<int:id>/', views.shop_detail, name='shop_detail'),
    path('nearby-shops/', views.nearby_shops, name='nearby_shops'),

    # booking system urls
    path("shop/<int:shop_id>/cart/", views.bookingSystem, name="shopping-cart"),  # URL for the booking system
    path('add/service/shop/<int:shop_id>/service/<int:service_id>/', views.add_service_to_cart, name='add_service_to_cart'),  # URL to add a service to the cart
    path('remove/service/shop/<int:shop_id>/service/<int:service_id>/', views.remove_service_from_cart, name='remove_service_from_cart'), # URL to remove a service from the cart
    path('select-professional/', views.choose_staff, name='choose_professional'), # choose a staff member to book a service
    path('select-professional/select-time-date/', views.select_date_and_time, name='select_time_date'),
    path('remove/services/', views.mobile_remove_servies_cart, name='mobile_remove_services_cart'),  # URL to remove services from the cart on mobile
    path('select-professional/select-slot/', views.select_slot, name='haris'),  # URL select_slot
    path('booking/confirm/', views.booking_confirmed, name='booking_confirmed'),  # URL for booking confirmation

]
    