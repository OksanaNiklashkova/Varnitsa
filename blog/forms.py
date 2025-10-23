from django import forms
from blog.models import Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ["title", "rubric", "text", "preview", "is_published", "publication_type"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "rubric": forms.TextInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "publication_type": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["publication_type"].help_text = 'Выберите тип публикации: "Статья для блога" или "Заметка"'


# Форма с несколькими отдельными полями для фото
class MultiplePhotoForm(forms.Form):
    image_1 = forms.ImageField(required=False, label="Фото 1", widget=forms.FileInput(attrs={"class": "form-control"}))
    image_2 = forms.ImageField(required=False, label="Фото 2", widget=forms.FileInput(attrs={"class": "form-control"}))
    image_3 = forms.ImageField(required=False, label="Фото 3", widget=forms.FileInput(attrs={"class": "form-control"}))
    image_4 = forms.ImageField(required=False, label="Фото 4", widget=forms.FileInput(attrs={"class": "form-control"}))

    def get_images(self):
        """Метод для получения списка изображений из формы"""
        images = []
        for i in range(1, 5):
            field_name = f"image_{i}"
            if hasattr(self, "cleaned_data") and field_name in self.cleaned_data and self.cleaned_data[field_name]:
                images.append(self.cleaned_data[field_name])
        return images
