from decimal import Decimal
from catalog.models import Product
from .models import DiscountCode, CartItem

# Il carrello è salvato in sessione per gli utenti non loggati. Dopo che fanno l'accesso viene salvato nel db
# Il carrello è un dizionario indicizzato sull'id dei prodotti che contiene la quantità e il prezzo
# I prodotti vengono presi dal db quando si itera dal carrello
class Cart:
    # Se non esiste, crea il dizionario cart
    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        
        if self.user.is_authenticated:
            # Se ci sono elementi nel carrello della sessione (carrello di utente non loggato), vengono uniti al db
            session_cart = self.session.get('cart')
            if session_cart:
                for product_id, item in session_cart.items():
                    cart_item, created = CartItem.objects.get_or_create(
                        user=self.user,
                        product_id=int(product_id),
                        defaults={'quantity': item['quantity']}
                    )
                    if not created:
                        cart_item.quantity += item['quantity']
                        cart_item.save()
                # Rimuovo il carrello dalla sessione una volta unito
                if 'cart' in self.session:
                    del self.session['cart']
                    self.session.modified = True
            
            # Carico il carrello dal database
            self.cart = {}
            for db_item in CartItem.objects.filter(user=self.user):
                self.cart[str(db_item.product.id)] = {
                    'quantity': db_item.quantity,
                    'price': str(db_item.product.current_price)
                }
        else:
            cart = self.session.get('cart')
            if not cart:
                cart = self.session['cart'] = {}
            self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.current_price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # Salva il carrello nel DB o nella sessione dopo modifica
    def save(self):
        self.session.modified = True
        
        if self.user.is_authenticated:
            current_product_ids = [] # Tiene traccia degli id dei prodotti rimasti nel carrello
            for product_id_str, item in self.cart.items():
                p_id = int(product_id_str)
                CartItem.objects.update_or_create(
                    user=self.user,
                    product_id=p_id,
                    defaults={'quantity': item['quantity']}
                )
                current_product_ids.append(p_id)
            # Rimuovo dal DB gli elementi non più presenti nel carrello
            CartItem.objects.filter(user=self.user).exclude(product_id__in=current_product_ids).delete()
        else:
            self.session['cart'] = self.cart

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # Svuota il carrello, funziona chiamata dopo il checkout
    def clear(self):
        self.cart = {}
        if self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        if 'cart' in self.session:
            del self.session['cart']
        if 'discount_id' in self.session:
            del self.session['discount_id']
        self.save()

    def get_subtotal(self):
        return sum(item['total_price'] for item in self)
        
    def get_discount(self):
        discount_id = self.session.get('discount_id')
        if discount_id:
            discount = DiscountCode.objects.filter(id=discount_id).first()
            if discount:
                return discount
            else:
                self.session['discount_id'] = None
                self.save()
        return None

    def get_total_price(self):
        subtotal = self.get_subtotal()
        discount = self.get_discount()
        if discount:
            return max(Decimal('0'), subtotal - discount.calculate_discount(subtotal))
        return subtotal

    def get_total_items(self):
        return sum(item['quantity'] for item in self)

    # Permette di iterare sul carrello, ritornando i prodotti nel database
    def __iter__(self):
        product_ids = self.cart.keys()
        # Query per recuperare tutti i prodotti con quegli id
        products = Product.objects.filter(id__in=product_ids)
        
        for product in products:
            self.cart[str(product.id)]['product'] = product
            self.cart[str(product.id)]['price'] = str(product.current_price)

        elementi_carrello = []
        for item in self.cart.values():
            # if che esclude quelli eliminati dal database
            if 'product' in item: # Esclude i prodotti tolti dal db
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                elementi_carrello.append(item)
            
        return iter(elementi_carrello)

    # Ritorna numero totale di elementi nel carrello
    def __len__(self):
        return self.get_total_items()
