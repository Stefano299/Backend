from django.urls import path
from . import views

app_name = "dashboard"

# Questa app gestisce solo la dashboard e non ha modelli o form... sarebbe potuta benissimo essere inglobata dalle app catalog
# e orders, ma ho preferito così per ordine e chiarezza 
urlpatterns = [
    # Manager Dashboard
    path("", views.ManagerDashboardView.as_view(), name="manager_dashboard"),
    
    # Prodotti
    path("product/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    
    # Categorie
    path("category/add/", views.CategoryCreateView.as_view(), name="category_create"),
    path("category/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("category/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    
    # Ordini
    path("order/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="order_update"),
    path("order/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
    path("review/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    
    # Codici Sconto
    path("discount/add/", views.DiscountCodeCreateView.as_view(), name="discount_create"),
    path("discount/<int:pk>/edit/", views.DiscountCodeUpdateView.as_view(), name="discount_update"),
    path("discount/<int:pk>/delete/", views.DiscountCodeDeleteView.as_view(), name="discount_delete"),
]
