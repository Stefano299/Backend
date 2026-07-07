from django.contrib import admin
from .models import Product, Category, Order, OrderItem, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    list_filter = ('categories',)
    search_fields = ('name', 'description')

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username', 'product__name')