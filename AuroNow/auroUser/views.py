from django.shortcuts import render
from shops.models import ShopOwner, ServiceCategory,ShopImage



def base_layout(request):
    categories = ServiceCategory.objects.values_list('name', flat=True).distinct()
    addresses = ShopOwner.objects.values_list('address', flat=True).distinct()
    price_ranges = ["0-50", "51-100", "101-200", "200+"]
    
    shop_images= ["./static/images/hero.png","./static/images/hero1.jpg", "./static/images/hero3.jpeg","./static/images/hero1.jpg","./static/images/hero.png","./static/images/hero3.jpeg" ]
    
    # shops  =ShopOwner.objects.prefetch_related("images", "sevices").all()
    # featured_shops = []
    # for shop in shops:
    #     services = shop.services.all()  # Get all services for the shop
    #     images = shop.images.all()  # Get all images for the shop

    #     # Only add the shop if it has services
    #     if services:
    #         featured_shops.append({
    #             "name": shop.shop_name,
    #             "address": shop.address,
    #             "services": list(services.values("name", "price")),
    #             "images": list(images.values_list("image_url", flat=True)),  # Get only image URLs
    #         })
    

    context = {
        'categories': categories,
        'addresses': addresses,
        'price_ranges': price_ranges,
        'shop_images':shop_images
    }
    print("shop_images",*context["shop_images"])   
    return render(request, 'base_layout.html', context)

# search view send data to search results template from search bar
def search_results(request):
    category = request.GET.get('category', '').strip()
    shop_name = request.GET.get('shop_name', '').strip().lower()
    address = request.GET.get('address', '').strip().lower()
    price_range = request.GET.get('price', '').strip()

    # Get all shops
    shops = ShopOwner.objects.all()
    results = []

    for shop in shops:
        # ✅ Apply Name and Address filters FIRST
        if shop_name and shop_name not in shop.shop_name.lower():
            continue
        if address and address not in shop.address.lower():
            continue

        # ✅ Filter images using the correct field 'shop_email'
        shops_image = ShopImage.objects.filter(shop_email=shop.email)
        image_urls=[
                request.build_absolute_uri(image.image.url)
                for image in shops_image
                if image.image
        ]
        # ✅ Convert RelatedManager to QuerySet
        services = shop.services.all()


        # ✅ Apply Category and Price Filters on Services
        filtered_services = []
        for service in services:
            if category and service.category and service.category.name != category:
                continue
            if price_range:
                price_value = float(service.price)  # Convert Decimal to float
                price_min, price_max = map(float, price_range.split('-'))
                if not (price_min <= price_value <= price_max):
                    continue
            filtered_services.append({
                'category': service.category.name if service.category else "Unknown",
                'name': service.name,
                'price': service.price
            })

        # ✅ Only add shop if it has matching services
        if filtered_services:
            results.append({
                'name': shop.shop_name,
                'address': shop.address,
                'services': filtered_services,
                'images': image_urls,
            })

    return render(request, 'search_results.html', {'results': results})
