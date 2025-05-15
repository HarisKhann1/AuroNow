# ✅ COMMIT: Removed all debug print statements, cleaned up search filter logic,
# and added explanatory comments to each section for maintainability.

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from auroUser.models import RatingAndReviews
from shops.models import ShopOwner, ServiceCategory, ShopImage, Service
import h3

# ----------------------------
# Helper Function: Get Shop Data (for recommended shops)
# ----------------------------
def get_shop_data(limit=5):
    shops = ShopOwner.objects.all()[:limit]
    shops_data = []

    for shop in shops:
        # Fetch related shop images
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [image.shop_image.url for image in shop_images if image.shop_image]

        # Fetch distinct service categories
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

        # Fetch reviews and calculate average rating
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        # Append to shop data list
        shops_data.append({
            'id': shop.id,
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,
            'rating': avg_rating_of_shop,
        })

    return shops_data

# ----------------------------
# View: Base Layout with Filters and Recommended Shops
# ----------------------------
def base_layout(request):
    context = {
        'shops': get_shop_data(),
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    }
    return render(request, 'base_layout.html', context)

# ----------------------------
# H3 Geolocation Helpers
# ----------------------------
def geo_to_h3(lat, lon, resolution=9):
    return h3.latlng_to_cell(lat, lon, resolution)

def get_h3_indexes_within_radius(user_h3, radius_cells):
    return h3.grid_disk(user_h3, radius_cells)

# ----------------------------
# View: Search Results with Filters and Nearby H3 Radius
# ----------------------------
def search_results(request):
    # Extract geolocation and filters
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip(),
        'city': request.GET.get('city', '').strip(),
        'price_range': request.GET.get('price', '').strip(),
    }

    # Validate coordinates
    try:
        user_lat = float(lat) if lat else None
        user_lon = float(lon) if lon else None
    except ValueError:
        user_lat = user_lon = None

    # Find nearby shops using H3 if coordinates provided
    if user_lat is not None and user_lon is not None:
        user_h3 = geo_to_h3(user_lat, user_lon)
        radius_cells_list = [0, 1, 2, 3]  # Expanding search from 0m to ~2km
        nearby_shop_ids = set()
        all_shops = ShopOwner.objects.filter(latitude__isnull=False, longitude__isnull=False)

        for radius_cells in radius_cells_list:
            nearby_cells = get_h3_indexes_within_radius(user_h3, radius_cells)
            for shop in all_shops:
                shop_h3 = geo_to_h3(shop.latitude, shop.longitude)
                if shop_h3 in nearby_cells:
                    nearby_shop_ids.add(shop.id)

        # If no shops found in any radius, render empty results
        if not nearby_shop_ids:
            return render(request, 'search_results.html', {
                'results': [],
                'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
                'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
                'price_ranges': ["0-50", "51-100", "101-200", "200+"],
            })

        # Filter to only nearby shops
        shops = ShopOwner.objects.filter(id__in=nearby_shop_ids)
    else:
        # Fallback: get all shops if no location given
        shops = ShopOwner.objects.all()

    # Apply filters: name, city, category
    if query['shop_name']:
        shops = shops.filter(shop_name__icontains=query['shop_name'])
    if query['city']:
        shops = shops.filter(city__icontains=query['city'])
    if query['category']:
        shops = shops.filter(categories__name__iexact=query['category'])

    filtered_shops = []
    for shop in shops.distinct():
        services = Service.objects.filter(shop=shop)

        # Apply price range filter
        if query['price_range']:
            try:
                if query['price_range'].endswith('+'):
                    min_price = float(query['price_range'][:-1])
                    services = services.filter(price__gte=min_price)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    services = services.filter(price__gte=min_p, price__lte=max_p)
            except ValueError:
                pass  # Ignore invalid price format

        # Only include shop if it has matching services
        if services.exists():
            filtered_shops.append(shop)

    # Build results context
    results = []
    for shop in filtered_shops:
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [img.shop_image.url for img in shop_images if img.shop_image]
        categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()
        customer_rating_list = RatingAndReviews.objects.filter(shop=shop)
        customer_rating_count = customer_rating_list.count()
        avg_rating = customer_rating_list.aggregate(Avg('rating'))
        avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

        results.append({
            'id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': customer_rating_count,
            'rating': avg_rating_of_shop,
        })

    return render(request, 'search_results.html', {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'cities': ShopOwner.objects.values_list('city', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    })

# ----------------------------
# View: Shop Detail Page
# ----------------------------
def shop_detail(request, id):
    # Fetch shop with related data to avoid multiple DB hits
    shop = get_object_or_404(
        ShopOwner.objects.prefetch_related(
            'services', 'staff', 'timings', 'images',
        ),
        id=id
    )

    # Get shop images
    shop_images = shop.images.all()
    image_urls = [img.shop_image.url for img in shop_images if img.shop_image]

    # Get categories
    categories = ServiceCategory.objects.filter(services__shop=shop).values_list('name', flat=True).distinct()

    # Get services and staff
    services = shop.services.all().select_related('category')
    staff_members = shop.staff.filter(is_active=True)

    # Get shop timings ordered by day
    # Define the correct order
    WEEKDAY_ORDER = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    shop_timings = sorted(
        shop.timings.all(),
        key=lambda x: WEEKDAY_ORDER.index(x.day)
    )
    # print("shop_timings: ",shop_timings)
    # Get latest 5 reviews with user info
    customer_rating_list = RatingAndReviews.objects.filter(shop=shop).select_related('user').order_by('-id')
    customer_rating_count = customer_rating_list.count()
    avg_rating = customer_rating_list.aggregate(Avg('rating'))
    avg_rating_of_shop = round(avg_rating['rating__avg'], 1) if avg_rating['rating__avg'] is not None else 0

    # Prepare context
    context = {
        'id': shop.id,
        'shop': shop,
        'images': image_urls,
        'reviews': customer_rating_count,
        'rating': avg_rating_of_shop,
        'customer_rating_list': customer_rating_list[:5],
        'now': timezone.now(),
        'services': services,
        'staff_members': staff_members,
        'timings': shop_timings,
        'categories': categories if categories else ["General"],
    }

    return render(request, 'shop_detail.html', context)
