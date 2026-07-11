from django.contrib import admin
from .models import Order, OrderItem, DiscountCode, CartItem

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity')
    list_filter = ('product',)
    search_fields = ('product__name', 'order__id')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')
    list_filter = ('user',)
    search_fields = ('product__name', 'user__username')

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'amount')
    list_filter = ('discount_type',)
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'payment_method', 'get_total_cost', 'created', 'shipping_status')
    list_filter = ('shipping_status', 'created', 'payment_method')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')

