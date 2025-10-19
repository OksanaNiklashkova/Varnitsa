from django.db import models
from django.contrib.postgres.indexes import GinIndex

class Category(models.Model):
    """Модель для создания категорий продуктов"""
    category_name = models.CharField(max_length=150, verbose_name='Наименование')

    def __str__(self):
        return f'{self.category_name}'

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['category_name',]
        db_table = 'categories'



class Product(models.Model):
    """Модель для создания продуктов"""
    product_name = models.CharField(max_length=150, verbose_name='Наименование', blank=True)
    trade_mark = models.CharField(max_length=50, verbose_name='ТМ', blank=True)
    specification = models.TextField(default='', verbose_name='Характеристики', blank=True, null=True)
    description = models.TextField(default='', verbose_name='Описание', blank=True, null=True)
    image = models.ImageField(null=True, upload_to='images/', default='images/placeholder.png', verbose_name='Изображение', blank=True)
    category = models.ManyToManyField(Category, related_name='products', blank=True, verbose_name='Категория')
    alcoholic = models.BooleanField(default=True, verbose_name='Алкогольный')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')

    def __str__(self):
        return f'{self.product_name}'

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        ordering = ['product_name',]
        db_table = 'products'
        indexes = [
            GinIndex(fields=['product_name', 'trade_mark', 'specification', 'description']),
        ]
