from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Order(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('ricevuto', 'Ordine ricevuto'),
        ('spedizione', 'Spedizione'),
        ('transito', 'In transito'),
        ('consegna', 'In consegna'),
        ('consegnato', 'Consegnato'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
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

    # Voglio vengano mostrati in ordine decrescente per data di creazione
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Ordine {self.id} - {self.user.username}"

    def get_total_cost(self):
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
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='orders_orderitem_price_gte_zero'
            ),
        ]

    def __str__(self):
        return f"Articolo {self.id} dell'Ordine {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity
