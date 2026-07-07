from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', default='products/default.png', blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    
    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            from django.db.models import Avg
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

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

    def __str__(self):
        return f"Recensione di {self.user.username} per {self.product.name} ({self.rating}/5)"