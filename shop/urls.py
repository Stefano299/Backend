from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("catalog/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:product_id>/review/", views.add_review, name="add_review"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.order_created, name="order_created"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    
    # Manager Dashboard
    path("dashboard/", views.manager_dashboard, name="manager_dashboard"),
    
    # Prodotti
    path("dashboard/product/add/", views.product_create, name="product_create"),
    path("dashboard/product/<int:pk>/edit/", views.product_update, name="product_update"),
    path("dashboard/product/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("dashboard/wallet/transfer/", views.transfer_wallet, name="transfer_wallet"),
    
    # Categorie
    path("dashboard/category/add/", views.category_create, name="category_create"),
    path("dashboard/category/<int:pk>/edit/", views.category_update, name="category_update"),
    path("dashboard/category/<int:pk>/delete/", views.category_delete, name="category_delete"),
    
    # Ordini
    path("dashboard/order/<int:pk>/edit/", views.order_update, name="order_update"),
    path("dashboard/order/<int:pk>/delete/", views.order_delete, name="order_delete"),
    
    # PC Building
    path("builder/step/<int:step>/", views.pc_builder_step, name="pc_builder_step"),
    path("builder/summary/", views.pc_builder_summary, name="pc_builder_summary"),
    path("builder/clear/", views.pc_builder_clear, name="pc_builder_clear"),
]


