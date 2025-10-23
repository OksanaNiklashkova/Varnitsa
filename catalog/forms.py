from django import forms

from catalog.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "trade_mark",
            "specification",
            "description",
            "image",
            "category",
            "alcoholic",
            "is_published",
        ]
        widgets = {
            "specification": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "product_name": forms.TextInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "category": forms.CheckboxSelectMultiple(),
            "alcoholic": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
