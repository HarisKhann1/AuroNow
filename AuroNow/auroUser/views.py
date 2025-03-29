from django.shortcuts import render
from shops.models import ShopOwner, ServiceCategory, Service

def dashboard_view(request):
    categories = ServiceCategory.objects.values_list('name', flat=True).distinct()
    addresses = ShopOwner.objects.values_list('address', flat=True).distinct()
    # categories = Service.objects.values_list('category__name', flat=True).distinct()
    price_ranges = ["0-50", "51-100", "101-200", "200+"]

    context = {
        'categories': categories,
        'addresses': addresses,
        'price_ranges': price_ranges
    }
    return render(request, 'dashboard.html', context)

def search_view(request):
    category = request.GET.get('category', '').strip()
    shop_name = request.GET.get('shop_name', '').strip().lower()
    address = request.GET.get('address', '').strip().lower()
    price_range = request.GET.get('price', '').strip()

    print(f"User Inputs - Category: {category}, Shop Name: {shop_name}, Address: {address}, Price: {price_range}")

    # Get all shops
    shops = ShopOwner.objects.all()

    results = []

    for shop in shops:
        # ✅ Apply Name and Address filters FIRST
        if shop_name and shop_name not in shop.shop_name.lower():
            continue
        if address and address not in shop.address.lower():
            continue

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
                'services': filtered_services
            })

    print(f"Search Results: {results}")

    return render(request, 'search_results.html', {'results': results})