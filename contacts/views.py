from django.forms import forms
from django.urls import reverse_lazy
from django.views import generic

from contacts.forms import ContactForm
from contacts.models import ContactRequest, ContactAttachment
from contacts.services import send_notification_email


class ContactsPageView(generic.TemplateView):
    """ Основной контент страницы контактов """
    template_name = 'contacts/page.html'

class SuccessTemplateView(generic.TemplateView):
    template_name = 'contacts/success.html'

class ContactRequestCreateView(generic.CreateView):
    """Контроллер для создания обращения на сайте"""
    model = ContactRequest
    form_class = ContactForm
    template_name = 'contacts/request_form.html'
    success_url = reverse_lazy('contacts:success')

    def get_client_ip(self):
        """Получение IP адреса клиента"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def validate_files(self, files):
        """Валидация прикрепленных файлов"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
        max_size = 5 * 1024 * 1024  # 5MB

        for file in files:
            if file:
                # Ограничение размера файла
                if file.size > max_size:
                    raise forms.ValidationError(f"Размер файла '{file.name}' превышает 5MB")

                # Проверка типа файла
                if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                    raise forms.ValidationError(
                        f"Недопустимый формат файла '{file.name}'. Допустимые форматы: {', '.join(valid_extensions)}")

    def form_valid(self, form):
        # Валидируем файлы перед сохранением
        files = self.request.FILES.getlist('attachment')
        if files:
            self.validate_files(files)

        # Сохраняем обращение
        contact_request = form.save(commit=False)
        contact_request.ip_address = self.get_client_ip()
        contact_request.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        contact_request.save()

        # Обработка множественных файлов
        for file in files:
            attachment = ContactAttachment.objects.create(
                contact_request=contact_request,
                file=file
            )

        # Проверяем сохраненные вложения
        saved_attachments = contact_request.attachments.all()

        # Отправляем email
        send_notification_email(contact_request)

        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка невалидной формы"""
        return super().form_invalid(form)