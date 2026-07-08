from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.OrderCreatedView.as_view(), name="order_created"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:order_id>/", views.OrderDetailView.as_view(), name="order_detail"),
    
    # Manager Dashboard
    path("dashboard/", views.ManagerDashboardView.as_view(), name="manager_dashboard"),
    
    # Manager CRUD per orders
    path("dashboard/order/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="order_update"),
    path("dashboard/order/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
]
