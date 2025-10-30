from django import forms
from .models import ContactRequest
import time


class ContactForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"class": "honeypot"}))
    timestamp = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"class": "timestamp"}))

    class Meta:
        model = ContactRequest
        fields = ["request_type", "name", "email", "subject", "message", "consent_personal_data", "consent_newsletter"]
        labels = {
            "consent_personal_data": "Согласие на обработку персональных данных",
            "consent_newsletter": "Согласие на рассылку новостей",
            "request_type": "Тип обращения",
            "name": "Ваше имя",
            "email": "Email",
            "subject": "Тема сообщения",
            "message": "Сообщение",
        }
        widgets = {
            "request_type": forms.Select(attrs={"class": "form-select", "help-text": "Выберите тип обращения"}),
            "subject": forms.Textarea(
                attrs={"rows": 2, "class": "form-control", "help-text": "Введите тему сообщения"}
            ),
            "message": forms.Textarea(
                attrs={"rows": 10, "class": "form-control", "help-text": "Опишите вашу проблему или вопрос подробно"}
            ),
            "name": forms.TextInput(attrs={"class": "form-control", "help-text": "Ваше имя (необязательно)"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "help-text": "Введите ваш email для обратной связи"}
            ),
            "consent_personal_data": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "help-text": """Поставив галочку в этом пункте,
                    вы даете согласие на обработку ваших персональных данных""",
                }
            ),
            "consent_newsletter": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "help-text": "Отметьте, если хотите получать новости и уведомления",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем начальные значения для скрытых полей
        self.fields["timestamp"].initial = str(time.time())

    def clean_honeypot(self):
        """Проверка honeypot поля"""
        honeypot = self.cleaned_data.get("honeypot")
        if honeypot:
            raise forms.ValidationError("Спам-обнаружение сработало")
        return honeypot

    def clean_timestamp(self):
        """Проверка времени заполнения формы"""
        timestamp = self.cleaned_data.get("timestamp")
        if not timestamp:
            raise forms.ValidationError("Отсутствует временная метка")

        try:
            elapsed = time.time() - float(timestamp)
            if elapsed < 2:  # до 2 секунд вероятно бот
                raise forms.ValidationError("Форма заполнена слишком быстро")
            if elapsed > 3600:  # Форма заполнялась больше часа - вероятно устаревшая
                raise forms.ValidationError("Время заполнения формы истекло")
        except (ValueError, TypeError):
            raise forms.ValidationError("Неверный формат временной метки")

        return timestamp

    def clean_consent_personal_data(self):
        """Проверка наличия согласия на обработку персональных данных"""
        consent = self.cleaned_data.get("consent_personal_data")
        if not consent:
            raise forms.ValidationError("Необходимо согласие на обработку персональных данных")
        return consent
