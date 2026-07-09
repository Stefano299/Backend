from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from catalog.models import Product, Category, Review
from orders.models import Order, OrderItem, DiscountCode
from catalog.forms import ProductForm, CategoryForm
from orders.forms import OrderEditForm, DiscountCodeForm

class ManagerDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'dashboard/manager_dashboard.html'
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
        
        context['discounts'] = DiscountCode.objects.all()
        
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
    template_name = 'dashboard/entity_form.html'
    success_url = reverse_lazy('dashboard:manager_dashboard')
    entity_title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_title'] = self.entity_title
        return context

class ManagerDeleteMixin(LoginRequiredMixin, PermissionRequiredMixin):
    #Mixin comune per le viste Delete del Manager.
    success_url = reverse_lazy('dashboard:manager_dashboard')
    http_method_names = ['post']

#----------- MANAGER CRUD -------------------

# --- Prodotti ---
class ProductCreateView(ManagerFormMixin, CreateView):
    model = Product
    form_class = ProductForm
    permission_required = 'catalog.add_product'
    entity_title = 'Prodotto'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Prodotto {self.object.name} creato con successo.")
        return response

class ProductUpdateView(ManagerFormMixin, UpdateView):
    model = Product
    form_class = ProductForm
    permission_required = 'catalog.change_product'
    entity_title = 'Prodotto'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Prodotto {self.object.name} aggiornato con successo.")
        return response

class ProductDeleteView(ManagerDeleteMixin, DeleteView):
    model = Product
    permission_required = 'catalog.delete_product'

    def form_valid(self, form):
        messages.success(self.request, f"Prodotto {self.object.name} eliminato.")
        return super().form_valid(form)

class ReviewDeleteView(ManagerDeleteMixin, DeleteView):
    model = Review
    permission_required = 'catalog.delete_review'

    def form_valid(self, form):
        messages.success(self.request, "Recensione eliminata con successo.")
        return super().form_valid(form)

# --- Categorie ---
class CategoryCreateView(ManagerFormMixin, CreateView):
    model = Category
    form_class = CategoryForm
    permission_required = 'catalog.add_category'
    entity_title = 'Categoria'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Categoria {self.object.name} creata.")
        return response

class CategoryUpdateView(ManagerFormMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    permission_required = 'catalog.change_category'
    entity_title = 'Categoria'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Categoria {self.object.name} aggiornata.")
        return response

class CategoryDeleteView(ManagerDeleteMixin, DeleteView):
    model = Category
    permission_required = 'catalog.delete_category'

    def form_valid(self, form):
        messages.success(self.request, f"Categoria {self.object.name} eliminata.")
        return super().form_valid(form)

# --- Ordini ---
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

class DiscountCodeCreateView(ManagerFormMixin, CreateView):
    model = DiscountCode
    form_class = DiscountCodeForm
    permission_required = 'orders.add_discountcode'
    entity_title = 'Codice Sconto'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Codice Sconto '{self.object.code}' creato con successo.")
        return response

class DiscountCodeUpdateView(ManagerFormMixin, UpdateView):
    model = DiscountCode
    form_class = DiscountCodeForm
    permission_required = 'orders.change_discountcode'
    entity_title = 'Codice Sconto'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Codice Sconto '{self.object.code}' aggiornato con successo.")
        return response

class DiscountCodeDeleteView(ManagerDeleteMixin, DeleteView):
    model = DiscountCode
    permission_required = 'orders.delete_discountcode'
    
    def form_valid(self, form):
        messages.success(self.request, f"Codice Sconto '{self.object.code}' eliminato con successo.")
        return super().form_valid(form)
