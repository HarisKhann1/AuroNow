from django.urls import path
from .views import base_layout, search_results, shop_detail, user_login, user_signup, logout_view, forget_password, user_reset_password ,nearby_shops

urlpatterns = [
    # authentication urls
    path('login/', user_login, name='user_login'),  # URL for user registration
    path('logout/', logout_view, name='user_logout'),  # URL for user logout
    path('signup/', user_signup, name='user_signup'),  # URL for user login
    path('forget-password/', forget_password, name='user_forget_password'),  # URL for password reset
    path('user/reset-password/<uuid:token>/', user_reset_password, name='user_reset_password'),
    
    # main urls
    path('', base_layout, name='base_layout'),  # URL for the base_layout
    path('search-results/', search_results, name='search_results'), 
    path('shop/<int:id>/', shop_detail, name='shop_detail'),
    path('nearby-shops/', nearby_shops, name='nearby_shops'),
]
    