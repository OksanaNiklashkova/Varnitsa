from django.contrib import admin

from catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category_name",
    )
    search_fields = ("category_name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "trade_mark",
        "specification",
        "description",
        "image",
        "alcoholic",
        "is_published",
    )
    list_filter = ["category"]
