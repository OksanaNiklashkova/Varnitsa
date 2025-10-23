from django.contrib import messages
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from blog.forms import PublicationForm, MultiplePhotoForm
from blog.models import Publication, Photo
from users.mixins import AgeVerificationRequiredMixin, ModeratorRequiredMixin


class PublicationListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер получения списка статей"""

    model = Publication
    template_name = "blog/publication_list.html"
    context_object_name = "publications"
    paginate_by = 10

    def get_queryset(self):
        """Метод получения списка статей с кешированием"""
        cache_key = "publications_queryset_v2"
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = self._get_fresh_queryset()
            cache.set(cache_key, queryset, 60 * 15)
        return queryset

    def _get_fresh_queryset(self):
        """Метод обновления списка статей"""
        return (
            Publication.objects.filter(is_published=True, publication_type="full")
            .prefetch_related("photos")
            .order_by("-created_at")
        )


# Сигналы для инвалидации кеша при изменении публикаций
@receiver([post_save, post_delete], sender=Publication)
def invalidate_publication_cache(sender, **kwargs):
    cache_keys = ["publications_queryset", "publications_queryset_v2"]
    for key in cache_keys:
        cache.delete(key)


@method_decorator(cache_page(60 * 15), name="dispatch")
class SmallPublicationListView(AgeVerificationRequiredMixin, ListView):
    """Контроллер получения списка заметок"""

    model = Publication
    template_name = "blog/small_publication_list.html"
    context_object_name = "publications"
    paginate_by = 10

    def get_queryset(self):
        return Publication.objects.filter(is_published=True, publication_type="small")


@method_decorator(cache_page(60 * 15), name="dispatch")
class PublicationDetailView(AgeVerificationRequiredMixin, DetailView):
    """Контроллер просмотра одной статьи"""

    model = Publication
    template_name = "blog/publication_detail.html"
    context_object_name = "publication"

    def get_queryset(self):
        return Publication.objects.prefetch_related("photos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["photos"] = self.object.photos.all()
        return context

    def get(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        response = super().get(request, *args, **kwargs)
        publication = self.get_object()
        publication.views_counter += 1
        publication.save()
        return response


class PublicationCreateView(ModeratorRequiredMixin, CreateView):
    """Контроллер создания новой статьи"""

    model = Publication
    form_class = PublicationForm
    template_name = "blog/publication_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:publication_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["multiple_photo_form"] = MultiplePhotoForm(self.request.POST, self.request.FILES)
        else:
            context["multiple_photo_form"] = MultiplePhotoForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        multiple_photo_form = context["multiple_photo_form"]

        # Сохраняем публикацию
        self.object = form.save()

        # Обрабатываем фото через метод get_images формы
        if multiple_photo_form.is_valid():
            images = multiple_photo_form.get_images()
            for image in images:
                Photo.objects.create(
                    publication=self.object, image=image, caption=f"Фото {self.object.photos.count() + 1}"
                )

        messages.success(self.request, "Статья успешно создана!")
        return super().form_valid(form)


class PublicationDeleteView(ModeratorRequiredMixin, DeleteView):
    """Контроллер удаления статьи"""

    model = Publication
    template_name = "blog/publication_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("blog:publication_list")


class PublicationUpdateView(ModeratorRequiredMixin, UpdateView):
    """Контроллер редактирования статьи"""

    model = Publication
    form_class = PublicationForm
    template_name = "blog/publication_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:publication_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["multiple_photo_form"] = MultiplePhotoForm(self.request.POST, self.request.FILES)
        else:
            context["multiple_photo_form"] = MultiplePhotoForm()
        context["existing_photos"] = self.object.photos.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        multiple_photo_form = context["multiple_photo_form"]

        self.object = form.save()

        # Обрабатываем фото через метод get_images формы
        if multiple_photo_form.is_valid():
            images = multiple_photo_form.get_images()
            for image in images:
                Photo.objects.create(
                    publication=self.object, image=image, caption=f"Фото {self.object.photos.count() + 1}"
                )

        messages.success(self.request, "Статья успешно обновлена!")
        return super().form_valid(form)


class PhotoDeleteView(ModeratorRequiredMixin, DeleteView):
    """Контроллер для удаления сохраненных изображений"""

    model = Photo
    template_name = "blog/photo_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("blog:publication_update", kwargs={"pk": self.object.publication.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Фотография удалена!")
        return super().delete(request, *args, **kwargs)
