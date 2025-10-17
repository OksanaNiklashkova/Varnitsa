from django.urls import path
from . import views
from contacts.apps import ContactsConfig

app_name = ContactsConfig.name

urlpatterns = [
    path('page/', views.ContactsPageView.as_view(), name='page'),
    path('request_form/', views.ContactRequestCreateView.as_view(), name='request_form'),
    path('success/', views.SuccessTemplateView.as_view(), name='success'),
]