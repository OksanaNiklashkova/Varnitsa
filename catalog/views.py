from django.shortcuts import render
from django.views.generic import TemplateView

from users.mixins import AgeVerificationRequiredMixin


class HomeView(AgeVerificationRequiredMixin, TemplateView):
    template_name = 'catalog/home.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['featured_beers'] = Beer.objects.filter(is_published=True)[:3]
    #     return context
