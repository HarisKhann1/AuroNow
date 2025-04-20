from django.shortcuts import render, get_object_or_404
from shops.models import ShopOwner, ServiceCategory, ShopImage
from random import randint, uniform

def get_shop_data(limit=5):
    shops = ShopOwner.objects.all()[:limit]
    shops_data = []
    for shop in shops:
        shop_images = ShopImage.objects.filter(shop_email=shop.email)
        image_urls = [image.image.url for image in shop_images if image.image]
        
        # Get categories from ServiceCategory model
        categories = [category.name for category in shop.categories.all()[:3]]

        shops_data.append({
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': str(randint(5, 50)),
            'rating': str(round(uniform(3.5, 5.0), 1)),
        })
    return shops_data

def base_layout(request):
    context = {
        'shops': get_shop_data(),
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    }
    return render(request, 'base_layout.html', context)

def search_results(request):
    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip().lower(),
        'address': request.GET.get('address', '').strip().lower(),
        'price_range': request.GET.get('price', '').strip(),
    }
    
    shops = ShopOwner.objects.all()
    if query['shop_name']:
        shops = shops.filter(shop_name__icontains=query['shop_name'])
    if query['address']:
        shops = shops.filter(address__icontains=query['address'])

    results = []
    for shop in shops:
        matched = False
        services = shop.services.all()
        if query['category']:
            services = services.filter(category__name=query['category'])
        if query['price_range']:
            filtered_services = []
            for service in services:
                price = float(service.price)
                if query['price_range'].endswith('+'):
                    if price >= float(query['price_range'][:-1]):
                        filtered_services.append(service)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    if min_p <= price <= max_p:
                        filtered_services.append(service)
            services = filtered_services

        if services:
            matched = True

        if matched:
            category_names = shop.categories.values_list('name', flat=True).distinct()[:3]
            results.append({
                'email': shop.email,
                'name': shop.shop_name,
                'address': shop.address,
                'images': [img.image.url for img in ShopImage.objects.filter(shop_email=shop.email) if img.image],
                'categories': list(category_names),
                'reviews': str(randint(5, 50)),
                'rating': str(round(uniform(3.5, 5.0), 1)),
            })

    return render(request, 'search_results.html', {'results': results})

def shop_detail(request, email):
    shop = get_object_or_404(ShopOwner, email=email)
    categories = [category.name for category in shop.categories.all()[:3]]
    
    return render(request, 'shop_detail.html', {
        'shop': shop,
        'images': [img.image.url for img in ShopImage.objects.filter(shop_email=email) if img.image],
        'categories': categories if categories else ["General"],
        'reviews': str(randint(5, 50)),  # Placeholder
        'rating': str(round(uniform(3.5, 5.0), 1)),  # Placeholder
    })
