from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from catalog.models import Product
from .models import Order, OrderItem, DiscountCode
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, DiscountApplyForm

# ------------------ CART -------------------------
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        
        # Questo codice controlla che uno non aggiunga al carrello piu elementi di quelli disponibili quando pigia "aggiungi al carrello",
        # serve in caso uno faccia ispezione elemento e in caso una persona, nel mentre, ha modificato lo stock comprando un prodotto
        # Controllo se il prodotto è già nel carrello
        product_id_str = str(product.id)
        if product_id_str in cart.cart:
            current_qty = cart.cart[product_id_str]['quantity']
        else:
            current_qty = 0
            
        # Calcolo la quantità che l'utente vuole mettere nel carrello
        if cd['override']:
            intended_qty = cd['quantity']
        else:
            intended_qty = current_qty + cd['quantity']
        
        if intended_qty > product.stock:
            messages.error(request, f"Impossibile aggiungere {intended_qty} unità. Solo {product.stock} di {product.name} disponibili.")
        else:
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
    discount_form = DiscountApplyForm()
    discount = cart.get_discount()
    discount_amount = discount.calculate_discount(cart.get_subtotal()) if discount else 0
    return render(request, 'orders/cart_detail.html', {
        'cart': cart,
        'discount_form': discount_form,
        'discount_amount': discount_amount
    })

@require_POST
@login_required
def discount_apply(request):
    cart = Cart(request)
    form = DiscountApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        discount = DiscountCode.objects.filter(code__iexact=code).first()
        
        if discount:
            # Controllo se lo user ha già usato questo codice sconto in passato
            if Order.objects.filter(user=request.user, discount_code=discount).exists():
                messages.error(request, f"Il codice sconto {code} è già stato utilizzato.")
            else:
                request.session['discount_id'] = discount.id
                cart.save()
                messages.success(request, f"Codice sconto {code} applicato con successo!")
        else:
            request.session['discount_id'] = None
            cart.save()
            messages.error(request, f"Codice sconto non valido.")
    return redirect('orders:cart_detail')

# ------------------CHECKOUT------------------------- 
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
            # Salva o aggiorna quelli inseriti nel profilo utente
            user_updated = False
            fields_to_update = [
                'first_name', 'last_name', 'email', 'indirizzo',
                'citta', 'codice_postale', 'numero_di_telefono'
            ]
            # Questo loop consente di evitare una enorme serie di if statement
            # Semplicemente cicla i campi del form e aggiorna l'utente se necessario 
            for field in fields_to_update:
                val = form.cleaned_data.get(field)
                if val and getattr(user, field) != val:
                    setattr(user, field, val)
                    user_updated = True
            if user_updated:
                user.save()
            
            # Controllo anche qua che l'utente non abbia nel carrello piu elementi di quelli disponibili (al checkout)
            # serve se, prima che uno faccia checkout, qualcun altro compra gli ultimi pezzi rimasti
            stock_error = False
            for item in cart:
                if item['quantity'] > item['product'].stock:
                    messages.error(request, f"Errore: {item['product'].name} ha solo {item['product'].stock} unità disponibili. Modifica il carrello.")
                    stock_error = True
            
            if stock_error:
                return redirect('orders:cart_detail')
            
            # Crea un ordine
            order = form.save(commit=False)
            order.user = user
            discount = cart.get_discount()
            if discount:
                order.discount_code = discount
                order.discount_amount = discount.calculate_discount(cart.get_subtotal())
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
            return redirect('orders:order_created', order_id=order.id)
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
        
    discount = cart.get_discount()
    discount_amount = discount.calculate_discount(cart.get_subtotal()) if discount else 0
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'form': form,
        'discount_amount': discount_amount
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
