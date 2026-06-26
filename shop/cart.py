from decimal import Decimal
from .models import Product

class Cart:
    # Se non esiste, crea il dizionario cart
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # Salva il carrello nella sessione dopo modifica
    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # Svuota il carrello
    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
            self.save()

    def get_total_price(self):
        return sum(item['total_price'] for item in self)

    def get_total_items(self):
        return sum(item['quantity'] for item in self)

    # Permette di iterare sul carrello, ritornando anche i prodotti nel database
    def __iter__(self):
        product_ids = self.cart.keys()
        # Query per recuperare tutti i prodotti con quegli id
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            # Si crea un dizionario annidato che contiene il prodotto preso dal database
            cart[str(product.id)]['product'] = product

        elementi_carrello = []
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            elementi_carrello.append(item)
            
        return iter(elementi_carrello)

    # Ritorna numero totale di elementi nel carrello
    def __len__(self):
        return self.get_total_items()
