from django.db.models import Avg, Count, Q
from django.db.models.functions import Coalesce

from auroUser.models import RatingAndReviews
from shops.models import ShopOwner, Service, ServiceCategory, ShopImage


def get_top_rated_shops_by_city(city, limit=8):
    """
    Get top rated shops by city with weighted ranking system.
    
    Args:
        city (str): The city name to filter shops
        limit (int): Number of shops to return (default: 8)
    
    Returns:
        list: List of dictionaries containing shop information
    """
    
    # Get shops in the specified city with their ratings and review counts
    shops_with_ratings = ShopOwner.objects.filter(
        city__icontains=city,
        shop_status_bool=True,  # Only active shops
        reviews__isnull=False  # Only shops with reviews
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    ).filter(
        review_count__gt=0  # Ensure shops have at least one review
    )
    
    # Calculate weighted score for each shop
    shop_scores = []
    for shop in shops_with_ratings:
        # Weighted score formula: (avg_rating * review_count) / (review_count + 5)
        # The +5 acts as a smoothing factor to prevent shops with very few reviews from dominating
        confidence_weight = shop.review_count / (shop.review_count + 5)
        weighted_score = shop.avg_rating * confidence_weight + 2.5 * (1 - confidence_weight)
        
        # Alternative scoring method (you can choose which one works better):
        # weighted_score = (shop.avg_rating * shop.review_count + 2.5 * 5) / (shop.review_count + 5)
        
        shop_scores.append({
            'shop': shop,
            'avg_rating': round(shop.avg_rating, 2),
            'review_count': shop.review_count,
            'weighted_score': weighted_score
        })
    
    # Sort by weighted score in descending order
    shop_scores.sort(key=lambda x: x['weighted_score'], reverse=True)
    
    # Get top shops up to the limit
    top_shops = shop_scores[:limit]
    
    # Prepare the result list
    result = []
    for shop_data in top_shops:
        shop = shop_data['shop']
        
        # Get top 3 service categories for this shop
        top_service_categories = get_top_service_categories(shop)
        
        # Get the first shop image (or None if no images exist)
        shop_image = get_shop_image(shop)
        
        shop_info = {
            'shop_id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'shop_image': shop_image,
            'total_average_rating': shop_data['avg_rating'],
            'user_friendly_rating': format_user_friendly_rating(shop_data['avg_rating']),
            'top_3_service_categories': top_service_categories,
            'total_reviews_count': shop_data['review_count']
        }
        
        result.append(shop_info)
    
    return result


def get_top_service_categories(shop):
    """
    Get top 3 service categories for a shop based on the number of services.
    
    Args:
        shop (ShopOwner): The shop instance
    
    Returns:
        list: List of top 3 service category names, or ["General"] if no services
    """
    
    # Get service categories ordered by the count of services in each category
    categories = ServiceCategory.objects.filter(
        services__shop=shop
    ).annotate(
        service_count=Count('services')
    ).order_by('-service_count')[:3]
    
    if categories.exists():
        return [category.name for category in categories]
    else:
        return ["General"]


def format_user_friendly_rating(rating):
    """
    Convert decimal rating to user-friendly format.
    
    Args:
        rating (float): The decimal rating (e.g., 4.67)
    
    Returns:
        str: User-friendly rating format (e.g., "4.5" or "5.0")
    """
    if rating == 0.0:
        return "0.0"
    
    # Round to nearest 0.5
    rounded_rating = round(rating * 2) / 2
    
    # Format to show one decimal place
    return f"{rounded_rating:.1f}"


def get_shop_image(shop):
    """
    Get the first shop image for a shop.
    
    Args:
        shop (ShopOwner): The shop instance
    
    Returns:
        str or None: URL of the first shop image, or None if no images exist or image is null
    """
    try:
        # Get the first shop image
        shop_image = ShopImage.objects.filter(shop=shop).first()
        
        if shop_image and shop_image.shop_image:
            return shop_image.shop_image.url
        else:
            return None
    except:
        return None


def get_all_shops_by_city_with_fallback(city, limit=8):
    """
    Alternative function that includes shops without reviews as fallback.
    
    Args:
        city (str): The city name to filter shops
        limit (int): Number of shops to return (default: 8)
    
    Returns:
        list: List of dictionaries containing shop information
    """
    
    # First, get shops with reviews
    shops_with_reviews = get_top_rated_shops_by_city(city, limit)
    
    # If we don't have enough shops, fill with shops without reviews
    if len(shops_with_reviews) < limit:
        remaining_slots = limit - len(shops_with_reviews)
        
        # Get shop IDs that already have reviews
        reviewed_shop_ids = [shop['name'] for shop in shops_with_reviews]
        
        # Get shops without reviews
        shops_without_reviews = ShopOwner.objects.filter(
            city__icontains=city,
            shop_status_bool=True
        ).exclude(
            shop_name__in=reviewed_shop_ids
        )[:remaining_slots]
        
        # Add shops without reviews to the result
        for shop in shops_without_reviews:
            top_service_categories = get_top_service_categories(shop)
            shop_image = get_shop_image(shop)
            
            shop_info = {
                'shop_id': shop.id,
                'name': shop.shop_name,
                'address': shop.address,
                'shop_image': shop_image,
                'total_average_rating': 0.0,  # No rating yet
                'user_friendly_rating': format_user_friendly_rating(0.0),
                'top_3_service_categories': top_service_categories,
                'total_reviews_count': 0
            }
            
            shops_with_reviews.append(shop_info)
    
    return shops_with_reviews


# Example usage in a Django view:
"""
from django.http import JsonResponse
from .recommendation_system import get_top_rated_shops_by_city

def get_recommended_shops(request):
    city = request.GET.get('city', 'Karachi')
    
    try:
        recommended_shops = get_top_rated_shops_by_city(city)
        return JsonResponse({
            'success': True,
            'city': city,
            'shops': recommended_shops
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Or in Django REST Framework:
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_recommended_shops_api(request):
    city = request.query_params.get('city', 'Karachi')
    limit = int(request.query_params.get('limit', 8))
    
    try:
        recommended_shops = get_top_rated_shops_by_city(city, limit)
        return Response({
            'success': True,
            'city': city,
            'count': len(recommended_shops),
            'shops': recommended_shops
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
"""