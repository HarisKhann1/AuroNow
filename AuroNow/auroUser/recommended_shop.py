from django.db.models import Avg, Count
from .models import ShopOwner, RatingAndReviews, Service

def get_top_salons_by_city(city_name):
    # Step 1: Filter active shops in the specified city
    shops_in_city = ShopOwner.objects.filter(city__iexact=city_name, shop_status_bool=True)

    # Step 2: Annotate each shop with average rating and number of reviews
    shops_with_ratings = shops_in_city.annotate(
        avg_rating=Avg('reviews__rating'),
        num_reviews=Count('reviews')
    )

    # Step 3: Compute global average rating and average review count for Bayesian weighting
    C = shops_with_ratings.aggregate(city_avg_rating=Avg('avg_rating'))['city_avg_rating'] or 0
    m = shops_with_ratings.aggregate(city_avg_reviews=Avg('num_reviews'))['city_avg_reviews'] or 1

    # Step 4: Calculate weighted score and build response
    salon_list = []
    for shop in shops_with_ratings:
        v = shop.num_reviews
        R = shop.avg_rating or 0
        weighted_score = ((v / (v + m)) * R) + ((m / (v + m)) * C)

        # Get unique service categories offered by the shop
        categories_qs = Service.objects.filter(shop=shop).select_related('category').values_list('category__name', flat=True).distinct()
        categories = list(filter(None, categories_qs))  # Remove nulls if any

        salon_list.append({
            'id': shop.id,
            'name': shop.shop_name,
            'rating': round(weighted_score, 2),
            'total_reviews': v,
            'categories': categories,
        })

    # Step 5: Sort by score and return top 8
    top_salons = sorted(salon_list, key=lambda x: x['rating'], reverse=True)[:8]

    return top_salons
