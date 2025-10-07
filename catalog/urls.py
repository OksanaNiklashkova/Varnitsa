from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import HomeView

app_name = CatalogConfig.name
print(app_name)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
]