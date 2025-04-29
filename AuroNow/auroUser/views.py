from django.shortcuts import render, get_object_or_404
from shops.models import ShopOwner, ServiceCategory, ShopImage
from random import randint, uniform

# Helper function to get random shops data
def get_shop_data(limit=5):
    shops = ShopOwner.objects.all()[:limit]
    shops_data = []

    for shop in shops:
        # Get all images related to the shop
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [image.shop_image.url for image in shop_images if image.shop_image]

        # Get all service categories (no [:3] limitation)
        categories = list(shop.categories.values_list('name', flat=True))

        shops_data.append({
            'id': shop.id,
            'email': shop.email,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': str(randint(5, 50)),  # Random review count
            'rating': str(round(uniform(3.5, 5.0), 1)),  # Random rating between 3.5 to 5.0
        })
    
    return shops_data

# View for base layout showing recommended shops
def base_layout(request):
    context = {
        'shops': get_shop_data(),
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    }
    return render(request, 'base_layout.html', context)

# Search Results View
def search_results(request):
    # Capture query parameters
    query = {
        'category': request.GET.get('category', '').strip(),
        'shop_name': request.GET.get('shop_name', '').strip(),
        'address': request.GET.get('address', '').strip(),
        'price_range': request.GET.get('price', '').strip(),
    }

    print("Received Query Parameters:", query)

    # Start with all shops
    shops = ShopOwner.objects.all()

    # Filter by shop name if provided
    if query['shop_name']:
        shops = shops.filter(shop_name__icontains=query['shop_name'])

    # Filter by address if provided
    if query['address']:
        shops = shops.filter(address__icontains=query['address'])

    # Filter by category if provided
    if query['category']:
        shops = shops.filter(categories__name__iexact=query['category'])

    # Now filter by price
    filtered_shops = []

    for shop in shops.distinct():
        services = shop.services.all()

        # Apply price range filter if selected
        if query['price_range']:
            try:
                if query['price_range'].endswith('+'):
                    min_price = float(query['price_range'][:-1])
                    services = services.filter(price__gte=min_price)
                else:
                    min_p, max_p = map(float, query['price_range'].split('-'))
                    services = services.filter(price__gte=min_p, price__lte=max_p)
            except ValueError:
                print("Invalid price range format provided:", query['price_range'])

        # Only add the shop if it has services matching the price filter
        if services.exists():
            filtered_shops.append(shop)
        else:
            print(f"Shop '{shop.shop_name}' skipped due to no matching service prices.")

    # Build final results
    results = []

    for shop in filtered_shops:
        shop_images = ShopImage.objects.filter(shop=shop)
        image_urls = [img.shop_image.url for img in shop_images if img.shop_image]
        categories = list(shop.categories.values_list('name', flat=True))

        results.append({
            'id': shop.id,
            'name': shop.shop_name,
            'address': shop.address,
            'images': image_urls,
            'categories': categories if categories else ["General"],
            'reviews': str(randint(5, 50)),
            'rating': str(round(uniform(3.5, 5.0), 1)),
        })

    print("Total Results:", len(results))

    # Render the search results page
    return render(request, 'search_results.html', {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"],
    })

# View for individual shop detail
def shop_detail(request, id):
    # Fetch the shop or return 404 if not found
    shop = get_object_or_404(ShopOwner, id=id)

    # Get all service categories
    categories = list(shop.categories.values_list('name', flat=True))

    # Get shop images
    shop_images = ShopImage.objects.filter(shop=shop)
    image_urls = [img.shop_image.url for img in shop_images if img.shop_image]

    return render(request, 'shop_detail.html', {
        'shop': shop,
        'images': image_urls,
        'categories': categories if categories else ["General"],
        'reviews': str(randint(5, 50)),
        'rating': str(round(uniform(3.5, 5.0), 1)),
    })
