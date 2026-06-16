from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Order, OrderItem
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm

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

    # Filtro categoria (multiplo)
    category_ids = request.GET.getlist('categories')
    if category_ids:
        products = products.filter(categories__id__in=category_ids).distinct()

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
        "selected_categories": category_ids,
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


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('shop:cart_detail')
    
    user = request.user
    # In caso completi il pagamento
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Salva o aggiorna quelli inseriti
            user_updated = False
            if form.cleaned_data['indirizzo'] and user.indirizzo != form.cleaned_data['indirizzo']:
                user.indirizzo = form.cleaned_data['indirizzo']
                user_updated = True
            if form.cleaned_data['citta'] and user.citta != form.cleaned_data['citta']:
                user.citta = form.cleaned_data['citta']
                user_updated = True
            if form.cleaned_data['codice_postale'] and user.codice_postale != form.cleaned_data['codice_postale']:
                user.codice_postale = form.cleaned_data['codice_postale']
                user_updated = True
            if form.cleaned_data['numero_di_telefono'] and user.numero_di_telefono != form.cleaned_data['numero_di_telefono']:
                user.numero_di_telefono = form.cleaned_data['numero_di_telefono']
                user_updated = True
            if user_updated:
                user.save()
            
            # Crea un ordine
            order = form.save(commit=False)
            order.user = user
            order.paid = True 
            order.save()
            
            for item in cart:
                # Crea un order item per ogni prodotto nel carrello
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            cart.clear()
            return redirect('shop:order_created', order_id=order.id)
    else:
        # In caso contrario crea il form precompilato con i dati dell'utente
        initial_data = {
            'indirizzo': user.indirizzo,
            'citta': user.citta,
            'codice_postale': user.codice_postale,
            'numero_di_telefono': user.numero_di_telefono,
        }
        form = OrderCreateForm(initial=initial_data)
        
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form
    })


@login_required
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_created.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})