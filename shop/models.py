from django.db import models
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