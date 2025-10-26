from catalog.models import Product


def get_products_by_category(category):
    """сервисная функция, формирующая список продуктов выбранной категории"""
    products_by_category = Product.objects.filter(category=category, is_published=True).prefetch_related("category")
    return products_by_category
