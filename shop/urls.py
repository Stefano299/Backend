from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("catalog/", views.ProductListView.as_view(), name="product_list"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:product_id>/review/", views.add_review, name="add_review"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.OrderCreatedView.as_view(), name="order_created"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:order_id>/", views.OrderDetailView.as_view(), name="order_detail"),
    
    # Manager Dashboard
    path("dashboard/", views.ManagerDashboardView.as_view(), name="manager_dashboard"),
    
    # Prodotti
    path("dashboard/product/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("dashboard/product/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("dashboard/product/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),

    
    # Categorie
    path("dashboard/category/add/", views.CategoryCreateView.as_view(), name="category_create"),
    path("dashboard/category/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("dashboard/category/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    
    # Ordini
    path("dashboard/order/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="order_update"),
    path("dashboard/order/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
    path("dashboard/review/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    
    # PC Building
    path("builder/step/<int:step>/", views.pc_builder_step, name="pc_builder_step"),
    path("builder/summary/", views.pc_builder_summary, name="pc_builder_summary"),
    path("builder/clear/", views.pc_builder_clear, name="pc_builder_clear"),
]


