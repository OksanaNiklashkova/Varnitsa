from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """класс, определяющий пользователя приложения"""

    username = models.CharField(max_length=100, blank=True, null=True, unique=False)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email
