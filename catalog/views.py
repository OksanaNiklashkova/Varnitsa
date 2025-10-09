from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, DeleteView, ListView

from catalog.forms import ProductForm
from catalog.models import Product, Category
from catalog.services import get_products_by_category
from users.mixins import AgeVerificationRequiredMixin, ModeratorRequiredMixin


class HomeView(AgeVerificationRequiredMixin, TemplateView):
    template_name = 'catalog/home.html'

class ProductCreateView(ModeratorRequiredMixin, CreateView):
    """Контроллер для создания продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:products')

class ProductUpdateView(ModeratorRequiredMixin, UpdateView):
    """Контроллер для редактирования продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:products')

class ProductCardDetailView(AgeVerificationRequiredMixin, DetailView):
    """Контроллер для просмотра карточки продукта"""
    model = Product
    template_name = 'catalog/product_card.html'
    context_object_name = 'product'

class ProductDeleteView(ModeratorRequiredMixin, DeleteView):
    """Контроллер для удаления продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:products')

class ProductByCategoryListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер для просмотра списка продуктов одной категории"""
    model = Product
    template_name = 'catalog/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs['category']
        products_by_category = get_products_by_category(category_id)
        return products_by_category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs['category']
        context['current_category'] = get_object_or_404(Category, id=category)
        return context


class AllProductsListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер для просмотра всех продуктов"""
    model = Product
    template_name = 'catalog/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_published=True).prefetch_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = None
        return context