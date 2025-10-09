from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import HomeView, ProductCreateView, ProductUpdateView, ProductCardDetailView, ProductDeleteView, \
    ProductByCategoryListView, AllProductsListView

app_name = CatalogConfig.name
print(app_name)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('new/', ProductCreateView.as_view(), name='form'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='form'),
    path('product/<int:pk>/', ProductCardDetailView.as_view(), name='product'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='delete'),
    path('products/', AllProductsListView.as_view(), name='products'),
    path('products/<int:category>/', ProductByCategoryListView.as_view(), name='products'),
]