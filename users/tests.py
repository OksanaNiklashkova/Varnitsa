from django.test import TestCase, Client
from django.urls import reverse

from users.models import User


class UserTestBase(TestCase):
    """Базовый класс для тестов приложения users"""

    def setUp(self):
        # Создаем авторизованного пользователя-с правами модератора
        self.moderator = User.objects.create_user(
            username="moderator", password="modpass123", email="moderator@example.com"
        )
        self.client = Client()

    def set_age_verified(self):
        """Устанавливает возрастную проверку в сессии"""
        session = self.client.session
        session["age_verified"] = True
        session.save()

    def login_as_moderator(self):
        """Логинит модератора и устанавливает возрастную проверку"""
        self.client.force_login(self.moderator)
        self.set_age_verified()
        return True


class AgeGateViewTest(TestCase):
    def test_home_view_success(self):
        """Тест для контроллера проверки возраста"""
        session = self.client.session
        session["age_verified"] = False
        session.save()
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:age_gate"))


class MixinIntegrationTests(UserTestBase):
    """Тесты для миксинов приложения users"""

    # Без подтверждения возраста - редирект
    def test_age_verification_required_view(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:age_gate"))

        self.set_age_verified()
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)

    def test_moderator_required_view(self):
        self.set_age_verified()
        response = self.client.get(reverse("catalog:products"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("catalog/products.html")
        self.assertNotContains(response, "Добавить продукт")

        self.login_as_moderator()
        response = self.client.get(reverse("catalog:products"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("catalog/products.html")
        self.assertContains(response, "Добавить продукт")
