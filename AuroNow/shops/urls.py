from django.contrib.auth import views as auth_views
from django.urls import path
from shops import views
import uuid

urlpatterns = [
    # logout route
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard_login'), name='logout'),
    
    # auth routes
    path('signup/', views.dashboard_signup_view, name='dashboard_signup'),
    path('login/', views.dashboard_login_view, name='dashboard_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
    
    # dshboard:: dashboard home and services routes
    path('', views.dashboard_home, name='dashboard_home'),
    
    # dshboard:: shop-timing and services routes
    path('service/', views.dashboard_service_view, name='dashboard_service'),
    path('add-service/', views.add_service_view, name='dashboard_add_service'),
    path('edit-service/<int:id>/', views.edit_service_view, name='dashboard_edit_service'),
    path('delete-service/<int:id>/', views.delete_service_view, name='dashboard_delete_service'),
    path('add-shop-timing/', views.add_shop_timing, name='dashboard_add_shop_timing'),
    path('edit-shop-timing/<int:id>/', views.edit_shop_timing, name='dashboard_edit_shop_timing'),
    path('delete-shop-timing/<int:id>/', views.delete_shop_timing, name='dashboard_delete_shop_timing'),
    
    # dashboard:: upload shop images route
    path('upload-images/', views.dashboard_images_upload_view, name='dashboard_upload_images'),
    path('delete-image/<int:id>/', views.delete_shop_image_view, name='dashboard_delete_image'),
    path('edit-image/<int:id>/', views.edit_shop_image_view, name='dashboard_edit_image'),
    
    # dashboard:: add staff routes
    path('staff/', views.dashboard_add_staff_view, name='dashboard_staff'),
    path('edit-staff/<int:id>/', views.dashboard_edit_staff_view, name='dashboard_edit-staff'),
    path('delete-staff/<int:id>/', views.dashboard_delete_staff_view, name='dashboard_delete-staff'),
    
    # dashboard:: add FAQs routes
    path('faq/', views.dashboard_faqs_view, name='dashboard_faq'),
    path('edit-faq/<int:id>', views.dashboard_edit_faq_view, name='dashboard_edit_faq'),
    path('delete-faq/<int:id>', views.dashboard_delete_faq_view, name='dashboard_delete_faq'),
    
    # dashboard:: answer queries routes
    path('queries/', views.dashboard_queries_view, name='dashboard_queries'),
    path('answer-queries/<int:id>', views.dahboard_answer_queries_view, name='dashboard_answer_queries'),
    path('delete-query/<int:id>', views.dashboard_delete_query_view, name='dashboard_delete_query'),
    
    # dashboard:: appointments routes
    path('appointments/', views.dashboard_appointments_view, name='dashboard_appointments'),
    path('confirm-appointment/<int:id>', views.dashboard_appointment_edit_view, name='dashboard_edit_appointment'),

    # dashboard:: dashboard profile routes
    path('profile', views.dashboard_profile, name='dashboard_profile'),
    path('edit-profile', views.update_profile, name='dashboard_edit_profile'),
    path('change-password', views.change_password, name='dashboard_change_password'),
    path('delete-profile', views.delete_profile, name='dashboard_delete_profile'),
]
