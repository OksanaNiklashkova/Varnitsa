from django import forms

from blog.models import Publication, Photo


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'text', 'preview', 'is_published']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption', 'order']