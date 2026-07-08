from django.shortcuts import render
from shop.models import Product

def homePageView(request):
    latest_products = Product.objects.all().order_by('-id')[:3]
    return render(request, "pages/home.html", {"products": latest_products})

def contactPageView(request):
    return render(request, "pages/contact.html")

