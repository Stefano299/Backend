from django.contrib import admin
from .models import Order, OrderItem, DiscountCode

admin.site.register(OrderItem)
admin.site.register(DiscountCode)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'created', 'shipping_status')
    list_filter = ('shipping_status', 'created')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
