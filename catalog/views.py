from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import ListView, DetailView
from .models import Product, Category, Review
from orders.models import user_has_purchased_product
from .forms import ReviewForm
from orders.forms import CartAddProductForm
from orders.cart import Cart


class ProductListView(ListView):
    model = Product
    template_name = "catalog/catalog.html"
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
            
        # Uso un match tatement al posto di una serie di if (da python 3.10 in poi)
        match sort_by:
            case 'price_asc':
                queryset = queryset.order_by('active_price', 'id')
            case 'price_desc':
                queryset = queryset.order_by('-active_price', 'id')
            case 'name_asc':
                queryset = queryset.order_by('name', 'id')
            case 'newest' | _:
                queryset = queryset.order_by('-id')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models.functions import Coalesce
        
        # Calcola prezzo massimo prodotti nel database
        # Coalescence, prendendo il primo valore non nullo, prende disocunt price se presente, sennò quello normale
        # Poi creo il campo virtuale active_price con annotate()
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
    template_name = "catalog/detail.html"
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
            has_purchased = user_has_purchased_product(self.request.user, product)
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
    has_purchased = user_has_purchased_product(request.user, product)
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
            
    return redirect('catalog:product_detail', pk=product.id)


# ------------------PC BUILDER (Quello per creare il PC in modo guidato)-------------------------

# Funzione helper che se trova categorie base mancanti ritorna un HttpResponseRedirect (il pc builder non può funzionare se manca una categoria base)
def _check_pc_builder_categories(request):
    categories_order = [
        'Processore', 'Dissipatore', 'Scheda Madre', 'Memoria RAM',
        'Scheda Video', 'Storage', 'Alimentatore', 'Case'
    ]
    missing_categories = [cat for cat in categories_order if not Category.objects.filter(name=cat).exists()]
    if missing_categories:
        missing_str = ", ".join(missing_categories)
        messages.error(request, f"Questa funzione non è più disponibile in quanto è stata eliminata una categoria base: {missing_str}")
        return redirect('home')
    return None

def pc_builder_step(request, step=1):
    categories_order = [
        'Processore', 'Dissipatore', 'Scheda Madre', 'Memoria RAM',
        'Scheda Video', 'Storage', 'Alimentatore', 'Case'
    ]
    
    redirect_response = _check_pc_builder_categories(request)
    if redirect_response:
        return redirect_response
            
    if step < 1 or step > len(categories_order):
        return redirect('catalog:pc_builder_step', step=1)
        
    current_cat_name = categories_order[step - 1]
    category = Category.objects.filter(name=current_cat_name).first()
    
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
            if "40" in gpu.name:
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
                return redirect('catalog:pc_builder_step', step=step + 1)
            else:
                return redirect('catalog:pc_builder_summary')
                
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
                
    return render(request, 'catalog/pc_builder_step.html', {
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
    redirect_response = _check_pc_builder_categories(request)
    if redirect_response:
        return redirect_response
        
    categories_order = [
        'Processore', 'Dissipatore', 'Scheda Madre', 'Memoria RAM',
        'Scheda Video', 'Storage', 'Alimentatore', 'Case'
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
            
    # Qua modifico direttamente l'oggetto carrello. Questo rafforza l'accoppiamento tra le app catalog e orders. Un'alternativa sarebbe potuta
    # essere quella di generare un form html gestito da orders. Mantengo così per semplicità (il progetto è già abbastanza complesso)
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
            
            return redirect('orders:cart_detail')
            
    return render(request, 'catalog/pc_builder_summary.html', {
        'selected_components': selected_components,
        'total_price': total_price,
        'missing_components': missing_components,
        'total_steps': len(categories_order),
    })

def pc_builder_clear(request):
    redirect_response = _check_pc_builder_categories(request)
    if redirect_response:
        return redirect_response
            
    # Cancella tutti i dati dell'assemblaggio salvati in sessione
    for i in range(1, 9):
        key = f'pc_build_step_{i}'
        if key in request.session:
            del request.session[key]
    request.session.modified = True
    return redirect('catalog:pc_builder_step', step=1)
