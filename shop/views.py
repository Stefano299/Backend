from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.views import View
from django.http import Http404
from .models import Product, Category, Order, OrderItem, Review
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, ProductForm, CategoryForm, OrderEditForm, ReviewForm


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
    
    # Carica le recensioni per questo prodotto
    reviews = product.reviews.all().order_by('-created_at')
    
    # Calcola la media delle recensioni
    if reviews.exists():
        from django.db.models import Avg
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        avg_rating = round(avg_rating, 1)
        stars_filled = range(int(round(avg_rating)))
        stars_empty = range(5 - int(round(avg_rating)))
    else:
        avg_rating = None
        stars_filled = None
        stars_empty = None
    
    # Verifica se l'utente può inserire una recensione (ha comprato il prodotto e non ha già recensito)
    can_review = False
    already_reviewed = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        can_review = has_purchased and not already_reviewed
        
    review_form = ReviewForm()
    
    return render(request, "shop/detail.html", {
        "product": product,
        "cart_product_form": cart_product_form,
        "reviews": reviews,
        "can_review": can_review,
        "already_reviewed": already_reviewed,
        "review_form": review_form,
        "avg_rating": avg_rating,
        "stars_filled": stars_filled,
        "stars_empty": stars_empty
    })

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Verifica che l'utente abbia acquistato e non abbia già inserito una recensione
    has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
    already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    
    if not has_purchased or already_reviewed:
        raise PermissionDenied("Non puoi recensire questo prodotto.")
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
    return redirect('shop:product_detail', pk=product.id)

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
            order.save()
            
            for item in cart:
                # Crea un order item per ogni prodotto nel carrello
                product = item['product']
                price = item['price']
                quantity = item['quantity']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=price,
                    quantity=quantity
                )
                # Se il prodotto ha un venditore associato, accreditiamo il ricavo nel suo wallet
                if product.seller:
                    seller = product.seller
                    seller.wallet_balance += price * quantity
                    seller.save()
            
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


from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps

# Queste due funzioni (fatte da IA), mi permettono di controllare i permessi in modo semplice.
# Sennò avrei usato degli if all'interno delle funzioni

def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.groups.filter(name='Store Manager').exists()):
            raise PermissionDenied("Accesso negato. Questa sezione è riservata ai manager.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def seller_or_manager_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.groups.filter(name__in=['Store Manager', 'Seller']).exists()):
            raise PermissionDenied("Accesso negato. Questa sezione è riservata a manager e venditori.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@seller_or_manager_required
def manager_dashboard(request):
    is_manager = request.user.is_staff or request.user.groups.filter(name='Store Manager').exists()
    
    if not is_manager and request.user.groups.filter(name='Seller').exists():
        # Il venditore vede solo i propri prodotti
        products = Product.objects.filter(seller=request.user)
        # Prodotti venduti (acquistati dagli altri)
        sales = OrderItem.objects.filter(product__seller=request.user).order_by('-order__created')
    else:
        products = Product.objects.all()
        # Per il manager, mostra tutti gli ordini registrati
        sales = OrderItem.objects.all().order_by('-order__created')
        
    categories = Category.objects.all()
    orders = Order.objects.all().order_by('-created')
    
    wallet_success = request.session.pop('wallet_success', None)
    wallet_error = request.session.pop('wallet_error', None)
    
    return render(request, 'shop/manager_dashboard.html', {
        'products': products,
        'categories': categories,
        'orders': orders,
        'sales': sales,
        'is_manager': is_manager,
        'wallet_success': wallet_success,
        'wallet_error': wallet_error
    })

@login_required
def transfer_wallet(request):
    if request.method == 'POST':
        try:
            from decimal import Decimal
            amount = Decimal(request.POST.get('amount', '0'))
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            request.session['wallet_error'] = "Importo non valido."
            return redirect('shop:manager_dashboard')
            
        user = request.user
        if user.wallet_balance >= amount:
            user.wallet_balance -= amount
            user.save()
            request.session['wallet_success'] = f"Trasferimento di €{amount} completato con successo!"
        else:
            request.session['wallet_error'] = "Fondi insufficienti nel wallet."
            
    return redirect('shop:manager_dashboard')

# --- Prodotti ---
@seller_or_manager_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # Assegna il venditore al prodotto (se l'utente è seller)
            if request.user.groups.filter(name='Seller').exists():
                product.seller = request.user
            product.save()
            form.save_m2m()
            return redirect('shop:manager_dashboard')
    else:
        form = ProductForm()
    return render(request, 'shop/entity_form.html', {'form': form, 'entity_title': 'Prodotto'})

@seller_or_manager_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Verifica che il venditore modifichi solo i propri prodotti
    is_manager = request.user.is_staff or request.user.groups.filter(name='Store Manager').exists()
    if not is_manager and product.seller != request.user:
        raise PermissionDenied("Non hai i permessi per modificare questo prodotto.")
        
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop:manager_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/entity_form.html', {'form': form, 'entity_title': 'Prodotto'})

@seller_or_manager_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Per sicurezza controllo sia is_staff che il gruppo
    is_manager = request.user.is_staff or request.user.groups.filter(name='Store Manager').exists()
    if not is_manager and product.seller != request.user:
        raise PermissionDenied("Non puoi eliminare questo prodotto")
        
    product.delete()
    return redirect('shop:manager_dashboard')

# --- Categorie ---
@manager_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:manager_dashboard')
    else:
        form = CategoryForm()
    return render(request, 'shop/entity_form.html', {'form': form, 'entity_title': 'Categoria'})

@manager_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('shop:manager_dashboard')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'shop/entity_form.html', {'form': form, 'entity_title': 'Categoria'})

@manager_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('shop:manager_dashboard')

# --- Ordini ---
@manager_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('shop:manager_dashboard')
    else:
        form = OrderEditForm(instance=order)
    return render(request, 'shop/entity_form.html', {'form': form, 'entity_title': 'Ordine'})

@manager_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect('shop:manager_dashboard')