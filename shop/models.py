from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name="Prezzo Scontato")
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', default='products/default.png', blank=True)
    
    categories = models.ManyToManyField(Category, related_name='products', blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='product_price_gte_zero'
            ),
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name='product_stock_gte_zero'
            ),
            models.CheckConstraint(
                check=models.Q(discount_price__lt=models.F('price')) | models.Q(discount_price__isnull=True),
                name='product_discount_price_lt_price'
            ),
        ]

    @property
    def current_price(self):
        if self.discount_price is not None:
            return self.discount_price
        return self.price

    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)
        return None

    def get_stars_filled(self):
        avg = self.get_average_rating()
        if avg is not None:
            return range(int(round(avg)))
        return []

    def get_stars_empty(self):
        avg = self.get_average_rating()
        if avg is not None:
            return range(5 - int(round(avg)))
        return []


class Order(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('ricevuto', 'Ordine ricevuto'),
        ('spedizione', 'Spedizione'),
        ('transito', 'In transito'),
        ('consegna', 'In consegna'),
        ('consegnato', 'Consegnato'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    indirizzo = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    codice_postale = models.CharField(max_length=20)
    numero_di_telefono = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, default='card')
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


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Rinforzo che un utente può lasciare una sola recensione per prodotto a livello di database
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Recensione di {self.user.username} per {self.product.name} ({self.rating}/5)"