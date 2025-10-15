from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

from .apps import UsersConfig
from .forms import CustomAuthenticationForm

app_name=UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(form_class=CustomAuthenticationForm, template_name="users/login.html"), name='login'),
    path('logout/', LogoutView.as_view(next_page='catalog:home'), name='logout'),
    path('', views.AgeGateView.as_view(), name='age_gate'),
]