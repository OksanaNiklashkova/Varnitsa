from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class AgeGateView(TemplateView):
    template_name = "users/age_gate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о текущем статусе проверки
        context["is_age_verified"] = self.request.session.get("age_verified", False)
        return context

    def post(self, request, *args, **kwargs):
        choice = request.POST.get("choice")

        if choice == "yes":
            request.session["age_verified"] = True
            request.session.set_expiry(60 * 60)  # 1 час
            next_page = request.GET.get("next", "catalog:home")
            return redirect(next_page)

        elif choice == "no":
            request.session["age_verified"] = False
            return render(request, self.template_name, {"error": True})

        return super().get(request, *args, **kwargs)
