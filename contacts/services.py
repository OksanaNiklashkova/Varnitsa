from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from config import settings
from contacts.models import ContactRequest


def get_recipients_by_type(contact_request):
    """Возвращает список email получателей в зависимости от типа обращения"""
    email_mapping = {
        ContactRequest.REVIEW: [
            'o.niklashkova@ptk-sm.ru',
        ],
        ContactRequest.PARTNERSHIP_SALES: [
            'o.niklashkova@ptk-sm.ru',
        ],
        ContactRequest.PARTNERSHIP_SUPPLY: [
            'o.niklashkova@ptk-sm.ru',
        ],
        ContactRequest.OTHER: [
            'o.niklashkova@ptk-sm.ru',
        ],
    }
    return email_mapping.get(contact_request.request_type, [settings.DEFAULT_FROM_EMAIL])


def send_notification_email(contact_request):
    try:
        email_recipients = get_recipients_by_type(contact_request)
        subject = f"Новое обращение: {contact_request.get_request_type_display()}"

        context = {
            'contact': contact_request,
            'site_url': 'http://localhost:8000',
        }

        html_message = render_to_string('contacts/notification.html', context)
        text_message = f"""
        Новое обращение с сайта Варница

        Тип: {contact_request.get_request_type_display()}
        Имя: {contact_request.name or 'Не указано'}
        Email: {contact_request.email}
        Тема: {contact_request.subject}
        Дата: {contact_request.created_at.strftime('%d.%m.%Y %H:%M')}

        Сообщение:
        {contact_request.message}

        Для просмотра в админ-панели: http://localhost:8000/admin/contacts/contactrequest/{contact_request.id}/change/
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=email_recipients,
            reply_to=[contact_request.email]
        )
        email.attach_alternative(html_message, "text/html")

        # Прикрепление файлов
        for attachment in contact_request.attachments.all():
            try:
                email.attach(attachment.file.name, attachment.file.read(), attachment.file.content_type)
            except Exception as e:
                print(f"Ошибка прикрепления файла {attachment.file.name}: {e}")

        email.send()

    except Exception as e:
        print(f"Ошибка отправки письма: {e}")