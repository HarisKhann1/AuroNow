from django.urls import path
from .views import dashboard_view, search_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),  # URL for the dashboard
    path('search-results/', search_view, name='search_results'),

]
