from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, DeleteView, ListView

from blog.models import Publication
from catalog.forms import ProductForm
from catalog.mixins import SearchMixin
from catalog.models import Product, Category
from catalog.services import get_products_by_category
from users.mixins import AgeVerificationRequiredMixin, ModeratorRequiredMixin


class HomeView(AgeVerificationRequiredMixin, TemplateView):
    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем новости для включения в шаблон
        from blog.models import Publication

        news_publications = (
            Publication.objects.filter(is_published=True, publication_type="news")
            .prefetch_related("photos")
            .order_by("-created_at")[:5]
        )
        context["news_publications"] = news_publications
        return context

    def get(self, request, *args, **kwargs):
        # Для аутентифицированных пользователей - без кеша
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)

        # Для анонимных - кешируем
        cache_key = f"home_page_{request.session.session_key}"
        cached_response = cache.get(cache_key)

        if cached_response is None:
            response = super().get(request, *args, **kwargs)
            # Рендерим только GET-запросы (не редиректы)
            if hasattr(response, "render"):
                response.render()
                cache.set(cache_key, response, 60 * 15)
            return response

        return cached_response


class ProductCreateView(ModeratorRequiredMixin, CreateView):
    """Контроллер для создания продукта"""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:products")


class ProductUpdateView(ModeratorRequiredMixin, UpdateView):
    """Контроллер для редактирования продукта"""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:products")


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProductCardDetailView(AgeVerificationRequiredMixin, DetailView):
    """Контроллер для просмотра карточки продукта"""

    model = Product
    template_name = "catalog/product_card.html"
    context_object_name = "product"


class ProductDeleteView(ModeratorRequiredMixin, DeleteView):
    """Контроллер для удаления продукта"""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:products")


class ProductByCategoryListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер для просмотра списка продуктов одной категории"""

    model = Product
    template_name = "catalog/products.html"
    context_object_name = "products"
    paginate_by = 10
    paginate_orphans = 2
    page_kwarg = "page"

    def get_queryset(self):
        """Метод получения списка продуктов по категории с кешированием"""
        category_id = self.kwargs["category"]
        cache_key = f"products_by_category_{category_id}_v2"
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = get_products_by_category(category_id)
            cache.set(cache_key, queryset, 60 * 15)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs["category"]
        context["current_category"] = get_object_or_404(Category, id=category)
        return context


class AllProductsListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер для просмотра всех продуктов"""

    model = Product
    template_name = "catalog/products.html"
    context_object_name = "products"
    paginate_by = 10
    paginate_orphans = 2
    page_kwarg = "page"

    def get_queryset(self):
        cache_key = "products_queryset_v2"
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Product.objects.filter(is_published=True).prefetch_related("category")
            cache.set(cache_key, queryset, 60 * 15)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_category"] = None
        return context


# Сигналы для инвалидации кеша при изменении списка продуктов по категории
@receiver([post_save, post_delete], sender=Product)
def invalidate_products_cache(sender, **kwargs):
    instance = kwargs.get("instance")
    cache_keys = [
        "products_queryset_v2",
    ]

    if instance and hasattr(instance, "category"):
        try:
            # Пробуем разные подходы
            if hasattr(instance.category, "all"):  # ManyToMany
                category_ids = instance.category.values_list("id", flat=True)
                for category_id in category_ids:
                    cache_keys.append(f"products_by_category_{category_id}_v2")
            else:  # ForeignKey
                cache_keys.append(f"products_by_category_{instance.category.id}_v2")
        except Exception as e:
            # Логируем ошибку, но не падаем
            print(f"Cache invalidation error: {e}")

    for key in cache_keys:
        cache.delete(key)


class SearchResultsView(SearchMixin, ListView):
    template_name = "catalog/search_results.html"
    context_object_name = "search_results"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()

        # Конфигурация моделей для поиска
        search_models = [
            {
                "model": Product,
                "fields": ["product_name", "trade_mark", "specification", "description"],
                "weight": "A",
            },
            {"model": Publication, "fields": ["title", "text", "rubric"], "weight": "A"},
        ]

        return self.perform_search(query, search_models)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["results_count"] = len(context["search_results"])
        return context
