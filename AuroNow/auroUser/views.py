from django.shortcuts import render
from django.http import HttpResponse
from shops.models import ShopOwner, Service, ServiceCategory

def dashboard_view(request):
    categories = ServiceCategory.objects.values_list('name', flat=True).distinct()
    addresses = ShopOwner.objects.values_list('address', flat=True).distinct()
    price_ranges = ["0-50", "51-100", "101-200", "200+"]

    context = {
        'categories': categories,
        'addresses': addresses,
        'price_ranges': price_ranges
    }
    return render(request, 'dashboard.html', context)

def search_view(request):
    category = request.GET.get('category', '').strip()
    shop_name = request.GET.get('shop_name', '').strip()
    address = request.GET.get('address', '').strip()
    price = request.GET.get('price', '').strip()

    query = ShopOwner.objects.all()

    if shop_name:
        query = query.filter(shop_name__icontains=shop_name)

    if address:
        query = query.filter(address__icontains=address)

    if category:
        query = query.filter(services__category__name__icontains=category).distinct()

    if price:
        try:
            if price == "200+":
                query = query.filter(services__price__gte=200).distinct()
            else:
                price_min, price_max = map(int, price.split('-'))
                query = query.filter(services__price__gte=price_min, services__price__lte=price_max).distinct()
        except ValueError:
            pass  # Ignore invalid price values

    results = []
    for shop in query:
        services = shop.services.values('category__name', 'name', 'price')
        results.append({
            'name': shop.shop_name,
            'address': shop.address,
            'services': list(services)
        })
    
    context = {
        'results': results,
        'categories': ServiceCategory.objects.values_list('name', flat=True).distinct(),
        'addresses': ShopOwner.objects.values_list('address', flat=True).distinct(),
        'price_ranges': ["0-50", "51-100", "101-200", "200+"]
    }
    return render(request, 'search_results.html', context)
