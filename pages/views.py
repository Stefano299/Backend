from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import Coalesce
from shop.models import Product

def homePageView(request):
    # Mostra i prodotti più venduti
    popular_products = Product.objects.annotate(
        total_sales=Coalesce(Sum('order_items__quantity'), 0)
    ).order_by('-total_sales', '-id')[:3]
    return render(request, "pages/home.html", {"products": popular_products})

