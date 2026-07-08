from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.models import Product, Category, Review
from catalog.mixins import ManagerFormMixin, ManagerDeleteMixin
from .models import Order, OrderItem
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, OrderEditForm

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
    return redirect('orders:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"{product.name} rimosso dal carrello.")
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'orders/cart_detail.html', {'cart': cart})


# ==========================================
# CHECKOUT & ORDERS
# ==========================================
@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('orders:cart_detail')
    
    user = request.user
    # In caso completi il pagamento
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            user_updated = False
            # Salva o aggiorna quelli inseriti nel profilo utente
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
                product = item['product']
                price = item['price']
                quantity = item['quantity']
                # Crea un order item per ogni prodotto nel carrello
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
            return redirect('orders:order_created', order_id=order.id)
    # In caso contrario crea il form precompilato con i dati dell'utente
    else:
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
        
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'form': form
    })

class OrderCreatedView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_created.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ==========================================
# MANAGER DASHBOARD 
# ==========================================
class ManagerDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'orders/manager_dashboard.html'
    permission_required = 'catalog.view_product'
    
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


# ==========================================
# MANAGER CRUD 
# ==========================================

class OrderUpdateView(ManagerFormMixin, UpdateView):
    model = Order
    form_class = OrderEditForm
    permission_required = 'orders.change_order'
    entity_title = 'Ordine'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Stato dell'ordine #{self.object.id} aggiornato.")
        return response

class OrderDeleteView(ManagerDeleteMixin, DeleteView):
    model = Order
    permission_required = 'orders.delete_order'

    def form_valid(self, form):
        messages.success(self.request, f"Ordine #{self.object.id} eliminato.")
        return super().form_valid(form)
