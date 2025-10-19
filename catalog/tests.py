from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from catalog.models import Product, Category
from blog.models import Publication
from catalog.mixins import SearchMixin
import tempfile
from PIL import Image
import json


class CatalogTestBase(TestCase):
    """Базовый класс для тестов каталога"""

    def setUp(self):
        # Создаем авторизованного пользователя-с правами модератора
        self.moderator = User.objects.create_user(
            username='moderator',
            password='modpass123',
            email='moderator@example.com'
        )

        # Создаем тестовые категории
        self.category1 = Category.objects.create(category_name='Разливные напитки')
        self.category2 = Category.objects.create(category_name='Фасованные напитки')

        # Создаем тестовое изображение
        image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image, 'JPEG')
        image.seek(0)

        # Создаем тестовое изображение для публикации
        preview_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        preview_img = Image.new('RGB', (100, 100), color='blue')
        preview_img.save(preview_image, 'JPEG')
        preview_image.seek(0)

        # Создаем тестовые продукты
        self.product1 = Product.objects.create(
            product_name='Пиво Темное',
            trade_mark='Варница',
            specification='Характеристики темного пива',
            description='Описание темного пива',
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=image.read(),
                content_type='image/jpeg'
            ),
            alcoholic=True,
            is_published=True
        )
        self.product1.category.add(self.category1)

        self.product2 = Product.objects.create(
            product_name='Лимонад',
            trade_mark='Варница',
            specification='Характеристики лимонада',
            description='Описание лимонада',
            alcoholic=False,
            is_published=True
        )
        self.product2.category.add(self.category2)

        # Создаем тестовую публикацию для поиска
        self.publication = Publication.objects.create(
            title='Новое пиво',
            text='Текст о новом пиве',
            rubric='Новости',
            preview=SimpleUploadedFile(
                name='test_preview.jpg',
                content=preview_image.read(),
                content_type='image/jpeg'
            ),
            is_published=True
        )

        self.client = Client()

    def set_age_verified(self):
        """Устанавливает возрастную проверку в сессии"""
        session = self.client.session
        session['age_verified'] = True
        session.save()

    def login_as_moderator(self):
        """Логинит модератора и устанавливает возрастную проверку"""
        self.client.force_login(self.moderator)
        self.set_age_verified()
        return True


class HomeViewTests(CatalogTestBase):
    """Тесты для главной страницы"""

    def test_home_view_success(self):
        """Тест статуса код главной страницы"""
        self.set_age_verified()
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/home.html')


class ProductCreateViewTests(CatalogTestBase):
    """Тесты для создания продукта"""

    def test_product_create_success(self):
        """Тест успешного создания продукта"""
        self.login_as_moderator()

        # Создаем изображение для формы
        image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img = Image.new('RGB', (100, 100), color='green')
        img.save(image, 'JPEG')
        image.seek(0)

        form_data = {
            'product_name': 'Новое пиво',
            'trade_mark': 'Варница',
            'specification': 'Новые характеристики',
            'description': 'Новое описание',
            'alcoholic': True,
            'is_published': True,
            'category': [self.category1.id],
            'image': SimpleUploadedFile(
                name='new_product.jpg',
                content=image.read(),
                content_type='image/jpeg'
            )
        }

        response = self.client.post(
            reverse('catalog:product_create'),
            data=form_data,
            follow=False  # Не следовать за редиректом
        )

        # После успешного создания должен быть редирект (302)
        self.assertEqual(response.status_code, 302)
        # Проверяем что редирект на правильную страницу
        self.assertEqual(response.url, reverse('catalog:products'))
        # Проверяем что продукт создался
        self.assertTrue(Product.objects.filter(product_name='Новое пиво').exists())


class ProductUpdateViewTests(CatalogTestBase):
    """Тесты для редактирования продукта"""

    def test_product_update_success(self):
        """Тест успешного обновления продукта"""
        self.login_as_moderator()
        url = reverse('catalog:product_update', kwargs={'pk': self.product1.pk})

        form_data = {
            'product_name': 'Обновленное пиво',
            'trade_mark': 'Обновленная ТМ',
            'specification': 'Обновленные характеристики',
            'description': 'Обновленное описание',
            'alcoholic': True,
            'is_published': True,
            'category': [self.category1.id, self.category2.id]
        }

        response = self.client.post(url, data=form_data, follow=False)

        # После успешного обновления должен быть редирект (302)
        self.assertEqual(response.status_code, 302)
        # Проверяем что редирект на правильную страницу
        self.assertEqual(response.url, reverse('catalog:products'))
        # Проверяем что продукт обновился
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.product_name, 'Обновленное пиво')


class ProductDeleteViewTests(CatalogTestBase):
    """Тесты для удаления продукта"""

    def test_product_delete_success(self):
        """Тест успешного удаления продукта"""
        self.login_as_moderator()
        url = reverse('catalog:product_delete', kwargs={'pk': self.product1.pk})

        response = self.client.post(url, follow=False)

        # После успешного удаления должен быть редирект (302)
        self.assertEqual(response.status_code, 302)
        # Проверяем что редирект на правильную страницу
        self.assertEqual(response.url, reverse('catalog:products'))
        # Проверяем что продукт удалился
        self.assertFalse(Product.objects.filter(pk=self.product1.pk).exists())

class ProductCardDetailViewTests(CatalogTestBase):
    """Тесты для просмотра карточки продукта"""

    def test_product_detail_view_success(self):
        """Тест статуса код страницы продукта"""
        self.set_age_verified()
        url = reverse('catalog:product', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_card.html')
        self.assertEqual(response.context['product'], self.product1)
        self.assertIn('product', response.context)

    def test_product_detail_view_404(self):
        """Тест 404 для несуществующего продукта"""
        self.set_age_verified()
        url = reverse('catalog:product', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProductByCategoryListViewTests(CatalogTestBase):
    """Тесты для списка продуктов по категории"""

    def test_category_products_view_success(self):
        """Тест статуса код страницы категории"""
        self.set_age_verified()
        url = reverse('catalog:category_products', kwargs={'category': self.category1.pk})
        response = self.client.get(url)
        products = response.context['products']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/products.html')
        self.assertIn('products', response.context)
        self.assertIn('current_category', response.context)
        self.assertEqual(response.context['current_category'], self.category1)
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first(), self.product1)

    def test_category_products_view_404(self):
        """Тест 404 для несуществующей категории"""
        self.set_age_verified()
        url = reverse('catalog:category_products', kwargs={'category': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class AllProductsListViewTests(CatalogTestBase):
    """Тесты для списка всех продуктов"""

    def test_all_products_view_status_code(self):
        """Тест статуса код страницы всех продуктов"""
        self.set_age_verified()
        response = self.client.get(reverse('catalog:products'))
        products = response.context['products']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/products.html')
        self.assertIn('products', response.context)
        self.assertIn('current_category', response.context)
        self.assertIsNone(response.context['current_category'])
        self.assertEqual(products.count(), 2)
        self.assertTrue(all(product.is_published for product in products))


class SearchResultsViewTests(CatalogTestBase):
    """Тесты для поиска"""

    @patch('catalog.views.SearchMixin.perform_search')
    def test_search_view_success(self, mock_perform_search):
        """Тест страницы поиска - общий"""
        mock_product = type('MockProduct', (), {'product_name': 'Пиво Test', 'rank': 0.5})()
        mock_publication = type('MockPublication', (), {'title': 'Статья о пиве', 'rank': 0.3})()

        mock_perform_search.return_value = [mock_product, mock_publication]

        self.set_age_verified()
        response = self.client.get(reverse('catalog:search_results') + '?q=пиво')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/search_results.html')
        self.assertIn('search_results', response.context)
        self.assertIn('query', response.context)
        self.assertIn('results_count', response.context)
        self.assertEqual(response.context['query'], 'пиво')
        self.assertEqual(len(response.context['search_results']), 2)  # Теперь есть результаты
        self.assertEqual(response.context['results_count'], 2)

    @patch('catalog.views.SearchMixin.perform_search')
    def test_search_empty_query(self, mock_perform_search):
        """Тест поиска с пустым запросом"""
        self.set_age_verified()
        mock_perform_search.return_value = []
        response = self.client.get(reverse('catalog:search_results') + '?q=')

        results = response.context['search_results']
        self.assertEqual(len(results), 0)

    @patch('catalog.views.SearchMixin.perform_search')
    def test_search_no_results(self, mock_perform_search):
        """Тест поиска без результатов"""
        self.set_age_verified()
        mock_perform_search.return_value = []
        response = self.client.get(reverse('catalog:search_results') + '?q=несуществующийзапрос')

        results = response.context['search_results']
        self.assertEqual(len(results), 0)
