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
    image_url = models.URLField(max_length=500, blank=True, default="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500")
    
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    indirizzo = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    codice_postale = models.CharField(max_length=20)
    numero_di_telefono = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, default='card')


    # Voglio vengano mostrati in ordine decrescente per data di creazione
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Ordine {self.id} - {self.user.username}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Articolo {self.id} dell'Ordine {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity