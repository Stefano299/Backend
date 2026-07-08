from decimal import Decimal
from .models import Product, DiscountCode

# Il carrello è un dizionario indicizzato sull'id dei prodotti che contiene la quantità e il prezzo
# I prodotti vengono presi dal db quando si itera dal carrello
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
            self.cart[product_id] = {'quantity': 0, 'price': str(product.current_price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # Salva il carrello nella sessione dopo modifica, necessario perchè django rileva quando riassegno una chiave di cart
    # ma non quando modifico il diizionario dentro il dizionario cart
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
            return max(Decimal('0'), subtotal - discount.amount)
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
