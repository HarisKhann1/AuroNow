from django.urls import path
from .views import base_layout, search_results, shop_detail

urlpatterns = [
    path('', base_layout, name='base_layout'),  # URL for the base_layout
    path('search-results/', search_results, name='search_results'), 
    path('shop/<int:id>/', shop_detail, name='shop_detail')
]
    