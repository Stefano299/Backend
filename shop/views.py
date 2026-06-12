from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max
from .models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Calcola prezzo massimo prodotti nel database
    risultato_aggregazione = Product.objects.aggregate(prezzo_massimo=Max('price'))
    max_db_price = risultato_aggregazione['prezzo_massimo']

    # Se non ci sono prodotti usa prezzo massimo di default
    if max_db_price:
        max_limit = int(max_db_price)
    else:
        max_limit = 1000

    # Filtro categoria
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(categories__id=category_id)

    # Ricerca
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Filtro prezzo 
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, "shop/catalog.html", {
        "products": products,
        "categories": categories,
        "selected_category": category_id,
        "search_query": search_query,
        "min_price": min_price,
        "max_price": max_price,
        "max_limit": max_limit,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_product_form = CartAddProductForm()
    return render(request, "shop/detail.html", {
        "product": product,
        "cart_product_form": cart_product_form
    })

def cart_add(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product,
                quantity=cd['quantity'],
                override_quantity=cd['override']
            )
    return redirect('shop:cart_detail')

def cart_remove(request, product_id):
    if request.method == 'POST':
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'shop/cart_detail.html', {'cart': cart})
