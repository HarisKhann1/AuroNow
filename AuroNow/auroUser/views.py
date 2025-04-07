from django.shortcuts import render
from shops.models import ShopOwner, ServiceCategory, ShopImage
from random import randint, uniform

def base_layout(request):
    categories = ServiceCategory.objects.values_list('name', flat=True).distinct()
    addresses = ShopOwner.objects.values_list('address', flat=True).distinct()
    price_ranges = ["0-50", "51-100", "101-200", "200+"]
    
    # Get recommended shops (you can modify this query as needed)
    recommended_shops = ShopOwner.objects.all()[:7]  # Get first 6 shops for demo
    
    # Prepare shop data with images and DEMO review data
    shops_data = []
    for shop in recommended_shops:
        # Get shop images
        shop_images = ShopImage.objects.filter(shop_email=shop.email)
        image_urls = [
            request.build_absolute_uri(image.image.url)
            for image in shop_images
            if image.image
        ]
        
        # Get shop services
        services = shop.services.all()[:3]  # Get first 3 services
        
        # Generate DEMO review data
        review_count = randint(5, 50)  # Random number of reviews between 5-50
        average_rating = round(uniform(3.5, 5.0), 1)  # Random rating between 3.5-5.0
        
        shops_data.append({
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'services':[ service.category.name if service.category else "Unknown"
                     for service in services
             ],
            'review_count': review_count,
            'average_rating': average_rating,
        })
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
    results = []

    for shop in shops:
        if shop_name and shop_name not in shop.shop_name.lower():
            continue
        if address and address not in shop.address.lower():
            continue

        shops_image = ShopImage.objects.filter(shop_email=shop.email)
        image_urls = [
            request.build_absolute_uri(image.image.url)
            for image in shops_image
            if image.image
        ]
        
        services = shop.services.all()
        
        # Generate DEMO review data for search results
        review_count = randint(5, 50)
        average_rating = round(uniform(3.5, 5.0), 1)

        filtered_services = []
        for service in services:
            if category and service.category and service.category.name != category:
                continue
            if price_range:
                price_value = float(service.price)
                if price_range.endswith('+'):
                    price_min = float(price_range[:-1])
                    if not (price_value >= price_min):
                        continue
                else:
                    price_min, price_max = map(float, price_range.split('-'))
                    if not (price_min <= price_value <= price_max):
                        continue
            filtered_services.append({
                'category': service.category.name if service.category else "Unknown",
                'name': service.name,
                'price': service.price
            })

        if filtered_services:
            results.append({
                'name': shop.shop_name,
                'address': shop.address,
                'services': filtered_services,
                'images': image_urls,
                'review_count': review_count,
                'average_rating': average_rating,
            })

    return render(request, 'search_results.html', {'results': results})