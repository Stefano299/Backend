from django.contrib import admin
from .models import Product, Category, Order, OrderItem, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Attributi visualizzati nel summary
    list_display = ('name', 'price', 'stock')
    # Attributi per il filtro laterale
    list_filter = ('categories',)
    # Attributi per la barra di ricerca
    search_fields = ('name', 'description')

admin.site.register(Category)
admin.site.register(OrderItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'created', 'shipping_status')
    list_filter = ('shipping_status', 'created')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username', 'product__name')