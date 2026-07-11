from django.contrib import admin
from .models import Product, Category, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Attributi visualizzati nel summary
    list_display = ('name', 'price', 'discount_price', 'stock')
    # Attributi per il filtro laterale
    list_filter = ('categories',)
    # Attributi per la barra di ricerca
    search_fields = ('name', 'description')

admin.site.register(Category)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username', 'product__name')
