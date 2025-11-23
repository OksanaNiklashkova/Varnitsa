import time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from contacts.models import ContactRequest
from users.models import User


class ContactsTestBase(TestCase):
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

    def make_contact_request(self):
        form_data = {
            "request_type": "review",
            "name": "Иван",
            "email": "oksana-za-40@yandex.ru",
            "subject": "Test subject",
            "message": "Test Test Test",
            "consent_personal_data": True,
            "consent_newsletter": True,
            "honeypot": "",
            "timestamp": str(time.time() - 10),
        }
        return form_data


class ContactsPageView(ContactsTestBase):
    """Тест основной страницы Контакты"""

    def test_contacts_page_success(self):
        self.set_age_verified()
        response = self.client.get(reverse("contacts:page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("contacts/page.html")


class ContactRequestCreateViewTests(ContactsTestBase):
    """Тесты для создания обращения"""

    def test_contact_request_not_valid(self):
        self.set_age_verified()
        form_data = self.make_contact_request()
        form_data["timestamp"] = str(time.time() - 1)
        self.client.post(reverse("contacts:request_form"), form_data)
        self.assertRaises(ValidationError)

        form_data.update({"timestamp": str(time.time() - 10), "consent_personal_data": False})
        response = self.client.post(reverse("contacts:request_form"), form_data)
        self.assertRaises(ValidationError)
        self.assertContains(response, "Необходимо согласие на обработку персональных данных")

        form_data.update({"consent_personal_data": True, "honeypot": "spam"})
        self.client.post(reverse("contacts:request_form"), form_data)
        self.assertRaises(ValidationError)

    @patch("contacts.views.send_notification_email")
    def test_contact_request_success(self, mock_send_email):
        self.set_age_verified()
        response = self.client.post(reverse("contacts:request_form"), self.make_contact_request())
        self.assertEqual(response.status_code, 302)
        # Редирект на страницу успешного отправления сообщения
        self.assertTemplateUsed("contacts/success.html")

        self.assertTrue(ContactRequest.objects.filter(email="oksana-za-40@yandex.ru").exists())
        self.assertTrue(mock_send_email.called)

    @patch("contacts.views.send_notification_email")
    def test_contact_request_with_attachments(self, mock_send_email):
        """Тест создания обращения с вложениями"""
        self.set_age_verified()

        # файл-вложение
        test_file1 = SimpleUploadedFile("test1.txt", b"file_content", content_type="text/plain")

        form_data = self.make_contact_request()
        form_data["attachment"] = test_file1

        response = self.client.post(reverse("contacts:request_form"), data=form_data, files={"attachment": test_file1})

        # Проверяем успешное создание
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactRequest.objects.filter(email="oksana-za-40@yandex.ru").exists())

        # Проверяем что вложения создались
        contact_request = ContactRequest.objects.get(email="oksana-za-40@yandex.ru")
        self.assertEqual(contact_request.attachments.count(), 1)

        # Проверяем вызов отправки email
        mock_send_email.assert_called_once_with(contact_request)
