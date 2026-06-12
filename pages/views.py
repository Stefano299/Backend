from django.shortcuts import render
from shop.models import Product

def homePageView(request):
    featured_products = Product.objects.all()[:3]
    return render(request, "pages/home.html", {"products": featured_products})

