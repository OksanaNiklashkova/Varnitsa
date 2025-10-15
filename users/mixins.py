from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class AgeVerificationRequiredMixin:
    """Миксин для проверки возраста"""

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('age_verified', False):
            messages.info(request, "Пожалуйста, подтвердите ваш возраст для доступа к сайту")
            return redirect('users:age_gate')
        return super().dispatch(request, *args, **kwargs)


class ModeratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для проверки прав модератора"""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "У вас нет прав для выполнения этого действия")
        return redirect('home')