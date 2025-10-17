from django.core.validators import FileExtensionValidator
from django.db import models


class ContactRequest(models.Model):
    """ Модель обратной связи от посетителей сайта """
    REVIEW = "review"
    PARTNERSHIP_SALES = "sales"
    PARTNERSHIP_SUPPLY = "supply"
    OTHER = "other"

    REQUEST_TYPES = [
        (REVIEW, "Хочу оставить отзыв"),
        (PARTNERSHIP_SALES, "Хочу продавать ваше пиво"),
        (PARTNERSHIP_SUPPLY, "Хочу предложить свой товар/услуги"),
        (OTHER, "У меня другой вопрос"),
    ]

    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default=REVIEW, verbose_name="Тип обращения")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя")
    email = models.EmailField(max_length=255, verbose_name="Email для связи")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    consent_personal_data = models.BooleanField(
        verbose_name="Согласие на обработку персональных данных",
        default=False
    )
    consent_newsletter = models.BooleanField(
        verbose_name="Согласие на рассылку",
        default=False
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP адрес")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.email}"

class ContactAttachment(models.Model):
    contact_request = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='contact_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
