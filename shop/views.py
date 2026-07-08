from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from .models import Product, Category, Order, OrderItem, Review
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, ProductForm, CategoryForm, OrderEditForm, ReviewForm


# ==========================================
# CATALOG & PRODUCTS
# ==========================================
class ProductListView(ListView):
    model = Product
    template_name = "shop/catalog.html"
    context_object_name = "products"
    paginate_by = 12  # Così non vengono mostrati tutti i prodotti nella stessa pagina

    def get_queryset(self):
        from django.db.models.functions import Coalesce
        queryset = super().get_queryset().annotate(
            active_price=Coalesce('discount_price', 'price')
        )
        
        # Filtro categoria (multiplo)
        category_ids = self.request.GET.getlist('categories')
        if category_ids:
            queryset = queryset.filter(categories__id__in=category_ids).distinct()

        # Ricerca
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # Filtro prezzo 
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(active_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(active_price__lte=max_price)
            
        # Ordinamento
        sort_by = self.request.GET.get('sort')
        if not sort_by:
            sort_by = 'newest'
            
        if sort_by == 'price_asc':
            queryset = queryset.order_by('active_price', 'id')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-active_price', 'id')
        elif sort_by == 'name_asc':
            queryset = queryset.order_by('name', 'id')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-id')
        else:
            queryset = queryset.order_by('-id')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcola prezzo massimo prodotti nel database
        from django.db.models.functions import Coalesce
        # Coalescence, prendendo il primo valore non nullo, prende disocunt price se presente, sennò quello normale
        # Poi creo il campo virtuale active_price con annotate
        most_expensive_product = Product.objects.annotate(
            active_price=Coalesce('discount_price', 'price')
        ).order_by('-active_price').first()
        max_db_price = most_expensive_product.active_price if most_expensive_product else 1000
        context['max_limit'] = int(max_db_price)
        
        context['categories'] = Category.objects.all()
        context['selected_categories'] = self.request.GET.getlist('categories')
        context['search_query'] = self.request.GET.get('q')
        context['min_price'] = self.request.GET.get('min_price')
        context['max_price'] = self.request.GET.get('max_price')
        context['sort_by'] = self.request.GET.get('sort', 'newest')
        
        # Costruisco la query string per mantenere i filtri nella paginazione
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            # Sennò si accumulano i numeri delle pagine
            del query_params['page']
        context['query_string'] = query_params.urlencode()
        
        if context.get('page_obj'):
            context['products'] = context['page_obj']
            
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        context['cart_product_form'] = CartAddProductForm()
        context['reviews'] = product.reviews.all().order_by('-created_at')
        
        # Verifica se l'utente può inserire una recensione
        can_review = False
        already_reviewed = False
        if self.request.user.is_authenticated:
            has_purchased = OrderItem.objects.filter(order__user=self.request.user, product=product).exists()
            already_reviewed = Review.objects.filter(product=product, user=self.request.user).exists()
            can_review = has_purchased and not already_reviewed
            
        context['can_review'] = can_review
        context['already_reviewed'] = already_reviewed
        context['review_form'] = ReviewForm()
        
        return context

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
            messages.success(request, f"La tua recensione per {product.name} è stata pubblicata!")
        else:
            messages.error(request, "Errore durante il salvataggio della recensione.")
            
    return redirect('shop:product_detail', pk=product.id)


# ==========================================
# CART
# ==========================================

@require_POST
def cart_add(request, product_id):
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
        messages.success(request, f"{product.name} aggiunto al carrello!")
    return redirect('shop:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"{product.name} rimosso dal carrello.")
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'shop/cart_detail.html', {'cart': cart})


# ==========================================
# CHECKOUT & ORDERS
# ==========================================

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
            # Salva o aggiorna quelli inseriti nel profilo utente
            user_updated = False
            if form.cleaned_data['first_name'] and user.first_name != form.cleaned_data['first_name']:
                user.first_name = form.cleaned_data['first_name']
                user_updated = True
            if form.cleaned_data['last_name'] and user.last_name != form.cleaned_data['last_name']:
                user.last_name = form.cleaned_data['last_name']
                user_updated = True
            if form.cleaned_data['email'] and user.email != form.cleaned_data['email']:
                user.email = form.cleaned_data['email']
                user_updated = True
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
                # Decrementa lo stock del prodotto
                product.stock -= quantity
                product.save()
            
            cart.clear()
            messages.success(request, "Ordine completato con successo!")
            return redirect('shop:order_created', order_id=order.id)
    else:
        # In caso contrario crea il form precompilato con i dati dell'utente
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
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

class OrderCreatedView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'shop/order_created.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shop/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'shop/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ==========================================
# PC BUILDER (Quello per creare il PC in modo guidato)
# ==========================================

def pc_builder_step(request, step=1):
    categories_order = [
        'Processore',
        'Dissipatore',
        'Scheda Madre',
        'Memoria RAM',
        'Scheda Video',
        'Storage',
        'Alimentatore',
        'Case'
    ]
    
    if step < 1 or step > len(categories_order):
        return redirect('shop:pc_builder_step', step=1)
        
    current_cat_name = categories_order[step - 1]
    category = Category.objects.filter(name=current_cat_name).first()
    if not category:
        raise Http404("Categoria non trovata")
    
    # Carica tutti i prodotti nel db per la categoria
    products = Product.objects.filter(categories=category, stock__gt=0)
    
    # Codice per simulare compabilità....
    selected_cpu_id = request.session.get('pc_build_step_1')
    selected_mobo_id = request.session.get('pc_build_step_3')
    selected_gpu_id = request.session.get('pc_build_step_5')
    
    compatibility_applied = False
    compatibility_details = "" # I dettagli sulla compabilità saranno visualizzati dall'utente nella pagina, in alto a sinistra
    cpu_name = None
    
    # Prende nome CPU se già selezionata
    if selected_cpu_id:
        cpu = Product.objects.filter(id=selected_cpu_id).first()
        if cpu:
            cpu_name = cpu.name

    # Nel secondo step, per il dissipatore toglie alcuni prodotti in base alla loro descrizione.
    # Prima controllo il tipo di CPU (AMD?), se sì tolgo quei dissipatori che simulo incompatibili
    if step == 2 and selected_cpu_id:
        cpu = Product.objects.filter(id=selected_cpu_id).first()
        if cpu:
            if "AMD" in cpu.name or "Ryzen" in cpu.name or "AMD" in cpu.description or "Ryzen" in cpu.description:
                compatibility_applied = True
                products = products.filter(description__icontains="AM5") | products.filter(description__icontains="AM4")
                compatibility_details = "Dissipatori compatibili con AMD"
            else:
                compatibility_applied = True
                products = products.exclude(description__icontains="AM5").exclude(description__icontains="AM4")
                compatibility_details = "Dissipatori compatibili con Intel"

    # Stessa cosa con scheda madre
    elif step == 3 and selected_cpu_id:
        cpu = Product.objects.filter(id=selected_cpu_id).first()
        if cpu:
            if "AMD" in cpu.name or "Ryzen" in cpu.name:
                compatibility_applied = True
                products = products.filter(description__icontains="AM5") | products.filter(description__icontains="AM4")
                compatibility_details = "Schede madri con socket AMD AM5"
            else:
                compatibility_applied = True
                products = products.exclude(description__icontains="AM5").exclude(description__icontains="AM4")
                compatibility_details = "Schede madri con socket Intel"
           
    # Per a memoria RAM controllo se la scheda madre supporta DDR4 o DDR5
    elif step == 4 and selected_mobo_id:
        mobo = Product.objects.filter(id=selected_mobo_id).first()
        if mobo:
            compatibility_applied = True
            if "DDR5" in mobo.name or "DDR5" in mobo.description:
                products = products.filter(description__icontains="DDR5")
                compatibility_details = "Memoria RAM DDR5 richiesta dalla scheda madre"
            else:
                products = products.filter(description__icontains="DDR4")
                compatibility_details = "Memoria RAM DDR4 richiesta dalla scheda madre"

    # Per l'alimentatore controllo se la scheda video è molto potente (nvidia serie 40)
    elif step == 7 and selected_gpu_id:
        gpu = Product.objects.filter(id=selected_gpu_id).first()
        if gpu:
            compatibility_applied = True
            # Controllo solo se contine 40 nel nome... (ovviamente potrebbe fallire, ma lo tengo semplice)
            if "40" in gpu.name:
                # Escludo gli alimentatori da 750W o inferiori per tenere solo quelli superiori
                products = products.exclude(description__icontains="450W")\
                                   .exclude(description__icontains="550W")\
                                   .exclude(description__icontains="650W")\
                                   .exclude(description__icontains="750W")
                compatibility_details = "Alimentatori superiori a 750W richiesti per GPU della serie 40"
            else:
                compatibility_details = "Alimentatori consigliati per la tua configurazione"
                
    # Salva componente in sessione
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id:
            request.session[f'pc_build_step_{step}'] = product_id
            request.session.modified = True
            
            # Passa allo step successivo o al riepilogo
            if step < len(categories_order):
                return redirect('shop:pc_builder_step', step=step + 1)
            else:
                return redirect('shop:pc_builder_summary')
                
    # Lista dei passaggi con i prodotti per il template (viene mostrato un summary in basso a desta)
    steps_data = []
    total_price = 0
    for i, cat_name in enumerate(categories_order, start=1):
        p_id = request.session.get(f'pc_build_step_{i}')
        prod = None
        if p_id:
            prod = Product.objects.filter(id=p_id).first()
            if prod:
                total_price += prod.current_price
        steps_data.append({
            'number': i,
            'name': cat_name,
            'product': prod,
            'is_current': (i == step),
            'is_completed': (prod is not None),
        })
                
    return render(request, 'shop/pc_builder_step.html', {
        'step': step,
        'total_steps': len(categories_order),
        'category_name': current_cat_name,
        'products': products,
        'steps_data': steps_data,
        'total_price': total_price,
        'compatibility_applied': compatibility_applied,
        'compatibility_details': compatibility_details,
        'cpu_name': cpu_name,
    })

def pc_builder_summary(request):
    categories_order = [
        'Processore',
        'Dissipatore',
        'Scheda Madre',
        'Memoria RAM',
        'Scheda Video',
        'Storage',
        'Alimentatore',
        'Case'
    ]
    
    # Recupera i componenti selezionati
    selected_components = []
    total_price = 0
    missing_components = False
    
    for i in range(1, len(categories_order) + 1):
        p_id = request.session.get(f'pc_build_step_{i}')
        if p_id:
            prod = Product.objects.filter(id=p_id).first()
            if prod:
                selected_components.append(prod)
                total_price += prod.current_price
            else:
                missing_components = True
        else:
            missing_components = True
            
    if request.method == 'POST':
        if not missing_components:
            # Aggiungo i prodotti selezionati al carrello
            cart = Cart(request)
            for prod in selected_components:
                cart.add(product=prod, quantity=1, override_quantity=False)
                
            # Svuoto la sessione del builder
            for i in range(1, len(categories_order) + 1):
                key = f'pc_build_step_{i}'
                if key in request.session:
                    del request.session[key]
            request.session.modified = True
            
            return redirect('shop:cart_detail')
            
    return render(request, 'shop/pc_builder_summary.html', {
        'selected_components': selected_components,
        'total_price': total_price,
        'missing_components': missing_components,
        'total_steps': len(categories_order),
    })

def pc_builder_clear(request):
    # Cancella tutti i dati dell'assemblaggio salvati in sessione
    for i in range(1, 9):
        key = f'pc_build_step_{i}'
        if key in request.session:
            del request.session[key]
    request.session.modified = True
    return redirect('shop:pc_builder_step', step=1)


# ==========================================
# MANAGER DASHBOARD & MIXINS
# ==========================================

class ManagerDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'shop/manager_dashboard.html'
    permission_required = 'shop.view_product'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Non sei autorizzato ad accedere alla dashboard.")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect('admin:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        
        orders = Order.objects.all().order_by('-created')
        context['orders'] = orders
        
        sales = OrderItem.objects.all().order_by('-order__created')
        context['sales'] = sales
        
        context['reviews'] = Review.objects.all().order_by('-created_at')
        
        context['total_sales_count'] = orders.count()
        context['total_earnings'] = sum(item.price * item.quantity for item in sales)
        
        # Serve soltanto per mostrare il numero di clienti nella dashboard...
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['total_customers'] = User.objects.filter(is_staff=False).exclude(groups__name='Store Manager').count()
        
        return context

# Creo due mixin per evitare di ripetere sempre le stesse righe, sfruttando le CBV
class ManagerFormMixin(LoginRequiredMixin, PermissionRequiredMixin):
    #Mixin comune per le viste Create/Update del Manager.
    template_name = 'shop/entity_form.html'
    success_url = reverse_lazy('shop:manager_dashboard')
    entity_title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_title'] = self.entity_title
        return context

class ManagerDeleteMixin(LoginRequiredMixin, PermissionRequiredMixin):
    #Mixin comune per le viste Delete del Manager.
    success_url = reverse_lazy('shop:manager_dashboard')
    http_method_names = ['post']


# ==========================================
# MANAGER CRUD 
# ==========================================

# --- Prodotti ---
class ProductCreateView(ManagerFormMixin, CreateView):
    model = Product
    form_class = ProductForm
    permission_required = 'shop.add_product'
    entity_title = 'Prodotto'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Prodotto {self.object.name} creato con successo.")
        return response

class ProductUpdateView(ManagerFormMixin, UpdateView):
    model = Product
    form_class = ProductForm
    permission_required = 'shop.change_product'
    entity_title = 'Prodotto'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Prodotto {self.object.name} aggiornato con successo.")
        return response

class ProductDeleteView(ManagerDeleteMixin, DeleteView):
    model = Product
    permission_required = 'shop.delete_product'

    def form_valid(self, form):
        messages.success(self.request, f"Prodotto {self.object.name} eliminato.")
        return super().form_valid(form)

class ReviewDeleteView(ManagerDeleteMixin, DeleteView):
    model = Review
    permission_required = 'shop.delete_review'

    def form_valid(self, form):
        messages.success(self.request, "Recensione eliminata con successo.")
        return super().form_valid(form)

# --- Categorie ---
class CategoryCreateView(ManagerFormMixin, CreateView):
    model = Category
    form_class = CategoryForm
    permission_required = 'shop.add_category'
    entity_title = 'Categoria'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Categoria {self.object.name} creata.")
        return response

class CategoryUpdateView(ManagerFormMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    permission_required = 'shop.change_category'
    entity_title = 'Categoria'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Categoria {self.object.name} aggiornata.")
        return response

class CategoryDeleteView(ManagerDeleteMixin, DeleteView):
    model = Category
    permission_required = 'shop.delete_category'

    def form_valid(self, form):
        messages.success(self.request, f"Categoria {self.object.name} eliminata.")
        return super().form_valid(form)

# --- Ordini ---
class OrderUpdateView(ManagerFormMixin, UpdateView):
    model = Order
    form_class = OrderEditForm
    permission_required = 'shop.change_order'
    entity_title = 'Ordine'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Stato dell'ordine #{self.object.id} aggiornato.")
        return response

class OrderDeleteView(ManagerDeleteMixin, DeleteView):
    model = Order
    permission_required = 'shop.delete_order'

    def form_valid(self, form):
        messages.success(self.request, f"Ordine #{self.object.id} eliminato.")
        return super().form_valid(form)