from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("catalog/", views.ProductListView.as_view(), name="product_list"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:product_id>/review/", views.add_review, name="add_review"),
    
    # PC builder
    path("builder/step/<int:step>/", views.pc_builder_step, name="pc_builder_step"),
    path("builder/summary/", views.pc_builder_summary, name="pc_builder_summary"),
    path("builder/clear/", views.pc_builder_clear, name="pc_builder_clear"),

    # Manager CRUD per products
    path("dashboard/product/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("dashboard/product/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("dashboard/product/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    
    # Manager CRUD per categories
    path("dashboard/category/add/", views.CategoryCreateView.as_view(), name="category_create"),
    path("dashboard/category/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("dashboard/category/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    
    # Manager CRUD per reviews
    path("dashboard/review/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
]
