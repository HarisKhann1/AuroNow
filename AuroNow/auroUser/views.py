from django.shortcuts import render , redirect, get_object_or_404
from shops.models import ShopOwner, ServiceCategory, ShopImage
from random import randint, uniform


def get_shop_data():
    recommended_shops = ShopOwner.objects.all()[:7]  # Get first 7 shops for demo
    shops_data = []
    for shop in recommended_shops:
        # Get shop images
        shop_images = ShopImage.objects.filter(shop_email=shop.email)
        image_urls = [
            image.image.url
            for image in shop_images
            if image.image
        ]
        
        # Get shop services
        services = shop.services.all()[:3]  # Get first 3 services
        
        # Generate DEMO review data
        review_count = randint(5, 50)  # Random number of reviews between 5-50
        average_rating = round(uniform(3.5, 5.0), 1)  # Random rating between 3.5-5.0
        
        shops_data.append({
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'services': [service.category.name if service.category else "Unknown" for service in services],
            'review_count': review_count,
            'average_rating': average_rating,
        })
    return shops_data


def get_categories_addresses_and_price_ranges():
    categories = ServiceCategory.objects.values_list('name', flat=True).distinct()
    addresses = ShopOwner.objects.values_list('address', flat=True).distinct()
    price_ranges = ["0-50", "51-100", "101-200", "200+"]
    return categories, addresses, price_ranges


def base_layout(request):
    # Get the shop-related data
    shops_data = get_shop_data()
    
    # Get the categories, addresses, and price ranges
    categories, addresses, price_ranges = get_categories_addresses_and_price_ranges()

    context = {
        'categories': categories,
        'addresses': addresses,
        'price_ranges': price_ranges,
        'shops': shops_data,
    }

    return render(request, 'base_layout.html', context)

def search_results(request):
    category = request.GET.get('category', '').strip()
    shop_name = request.GET.get('shop_name', '').strip().lower()
    address = request.GET.get('address', '').strip().lower()
    price_range = request.GET.get('price', '').strip()

    shops = ShopOwner.objects.all()

    if shop_name:
        shops = shops.filter(shop_name__icontains=shop_name)
    if address:
        shops = shops.filter(address__icontains=address)

    results = []
    
    for shop in shops:
        # Get shop images
        shop_images = ShopImage.objects.filter(shop_email=shop.email)
        image_urls = [
            request.build_absolute_uri(image.image.url)
            for image in shop_images
            if image.image
        ]
        
        services = shop.services.all()
        filtered_services = []
        
        for service in services:
            if category and service.category and service.category.name != category:
                continue
            if price_range:
                price_value = float(service.price)  # price is now a decimal, safely convert to float
                if price_range.endswith('+'):
                    price_min = float(price_range[:-1])  # Remove the '+' and convert to float
                    if not (price_value >= price_min):
                        continue
                else:
                    price_min, price_max = map(float, price_range.split('-'))  # Split for range and convert to float
                    if not (price_min <= price_value <= price_max):
                        continue
            filtered_services.append({
                'category': service.category.name if service.category else "Unknown",
                'name': service.name,
                'price': service.price
            })

        if filtered_services:
            review_count = randint(5, 50)
            average_rating = round(uniform(3.5, 5.0), 1)
            results.append({
                'email': shop.email,
                'name': shop.shop_name,
                'address': shop.address,
                'services': filtered_services,
                'images': image_urls,
                'review_count': review_count,
                'average_rating': average_rating,
            })

    return render(request, 'search_results.html', {'results': results})

def recntly_views (request, shop_id,):
    return render(request, "recently_views")


def shop_detail(request, email):
    shop = get_object_or_404(ShopOwner, email=email)
    
    # Fetch shop images
    shop_images = ShopImage.objects.filter(shop_email=email)
    image_urls = [image.image.url for image in shop_images if image.image]

    # Pass images along with shop data to the template
    return render(request, 'shop_detail.html', {'shop': shop, 'images': image_urls})
