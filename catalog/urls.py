from django.urls import path
from catalog.apps import CatalogConfig
from catalog import views

app_name = CatalogConfig.name

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("new/", views.ProductCreateView.as_view(), name="product_create"),
    path("update/<int:pk>/", views.ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/", views.ProductCardDetailView.as_view(), name="product"),
    path("delete/<int:pk>/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("products/", views.AllProductsListView.as_view(), name="products"),
    path("products/<int:category>/", views.ProductByCategoryListView.as_view(), name="category_products"),
    path("search/", views.SearchResultsView.as_view(), name="search_results"),
]
