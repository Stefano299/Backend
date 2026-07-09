from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/discount/", views.discount_apply, name="discount_apply"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.OrderCreatedView.as_view(), name="order_created"),
    path("", views.OrderListView.as_view(), name="order_list"),
    path("<int:order_id>/", views.OrderDetailView.as_view(), name="order_detail"),
]
