from django.urls import path
from .views import base_layout, search_results

urlpatterns = [
    path('', base_layout, name='base_layout'),  # URL for the base_layout
    path('search-results/', search_results, name='search_results'),

]
