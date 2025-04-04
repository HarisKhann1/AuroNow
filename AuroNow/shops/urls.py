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
    # dshboard routes
    path('', views.dashboard_home, name='dashboard_home'),
    path('service/', views.dashboard_service_view, name='dashboard_service'),
    path('add-category/', views.add_service_category_view, name='dashboard_add_category'),
    path('add-service/', views.add_service_view, name='dashboard_add_service'),
    path('edit-category/<int:id>/', views.edit_category_view, name='dashboard_edit_category'),
    path('delete-category/<int:id>/', views.delete_category_view, name='dashboard_delete_category'),
]
