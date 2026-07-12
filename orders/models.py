from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from catalog.models import Product

class DiscountCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fisso (€)'),
        ('percentage', 'Percentuale (%)'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="Codice Sconto")
    discount_type = models.CharField(
        max_length=15,
        choices=DISCOUNT_TYPE_CHOICES,
        default='fixed',
        verbose_name="Tipo di Sconto"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valore Sconto")
    
    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()}: {self.amount})"

    def calculate_discount(self, subtotal):
        from decimal import Decimal, ROUND_HALF_UP
        if self.discount_type == 'percentage':
            discount_val = (subtotal * self.amount) / Decimal('100')
            # Mi assicuro vengano mostrate max due cifre decimali
            discount_val = discount_val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return min(subtotal, discount_val)
        return min(subtotal, self.amount)

class Order(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('ricevuto', 'Ordine ricevuto'),
        ('spedizione', 'Spedizione'),
        ('transito', 'In transito'),
        ('consegna', 'In consegna'),
        ('consegnato', 'Consegnato'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    indirizzo = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    codice_postale = models.CharField(max_length=20)
    numero_di_telefono = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carta di Credito'),
        ('paypal', 'PayPal'),
        ('transfer', 'Bonifico Bancario'),
    ]
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='card',
        verbose_name="Metodo di Pagamento"
    )
    shipping_status = models.CharField(
        max_length=20,
        choices=SHIPPING_STATUS_CHOICES,
        default='ricevuto',
        verbose_name="Stato Spedizione"
    )
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Importo Sconto Applicato")

    # Voglio vengano mostrati in ordine decrescente per data di creazione
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Ordine {self.id} - {self.user.username}"

    def get_total_cost(self):
        total = sum(item.get_cost() for item in self.items.all())
        return max(0, total - self.discount_amount)

    def get_subtotal_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    # Serve alla barra di avanzamento della spedizione mostrata nel frontend
    def return_order_number(self):
        mapping = {
            'ricevuto': 1,
            'spedizione': 2,
            'transito': 3,
            'consegna': 4,
            'consegnato': 5,
        }
        return mapping.get(self.shipping_status, 1)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='orderitem_price_gte_zero'
            ),
        ]

    def __str__(self):
        return f"Articolo {self.id} dell'Ordine {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} del prodotto {self.product.name} di utente {self.user.username}"


# Funzione per verificare se un utente ha acquistato un prodotto in passato. 
# Viene usata nell'app catalog per sapere se l'utente può inserire una recensione,
# senza questa funzione avrei dovuto scrivere OrderItem.objects.filter(order__user=user, product=product).exists() 
# nella vista del catalog che avrebbe causato un forte accoppiamento tra le due app
def user_has_purchased_product(user, product):
    if not user or not user.is_authenticated:
        return False
    return OrderItem.objects.filter(order__user=user, product=product).exists()

