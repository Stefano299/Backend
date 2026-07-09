from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
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
    
    # Codici Sconto
    path("dashboard/discount/add/", views.DiscountCodeCreateView.as_view(), name="discount_create"),
    path("dashboard/discount/<int:pk>/edit/", views.DiscountCodeUpdateView.as_view(), name="discount_update"),
    path("dashboard/discount/<int:pk>/delete/", views.DiscountCodeDeleteView.as_view(), name="discount_delete"),
]
