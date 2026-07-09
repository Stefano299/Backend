from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:product_id>/review/", views.add_review, name="add_review"),
    
    # PC Building
    path("builder/step/<int:step>/", views.pc_builder_step, name="pc_builder_step"),
    path("builder/summary/", views.pc_builder_summary, name="pc_builder_summary"),
    path("builder/clear/", views.pc_builder_clear, name="pc_builder_clear"),
]
