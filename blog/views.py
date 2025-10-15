from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from blog.forms import PublicationForm, MultiplePhotoForm
from blog.models import Publication, Photo
from users.mixins import AgeVerificationRequiredMixin, ModeratorRequiredMixin


class PublicationListView(AgeVerificationRequiredMixin, ListView):
    model = Publication
    template_name = 'blog/publication_list.html'
    context_object_name = 'publications'
    paginate_by = 10

    def get_queryset(self):
        return Publication.objects.filter(is_published=True, publication_type='full').prefetch_related('photos')


class SmallPublicationListView(AgeVerificationRequiredMixin, ListView):
    model = Publication
    template_name = 'blog/small_publication_list.html'
    context_object_name = 'publications'
    paginate_by = 10

    def get_queryset(self):
        return Publication.objects.filter(is_published=True, publication_type='small')


class PublicationDetailView(AgeVerificationRequiredMixin, DetailView):
    model = Publication
    template_name = 'blog/publication_detail.html'
    context_object_name = 'publication'

    def get_queryset(self):
        return Publication.objects.prefetch_related('photos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        return context

    def get(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        response = super().get(request, *args, **kwargs)
        publication = self.get_object()
        publication.views_counter += 1
        publication.save()
        return response


class PublicationCreateView(ModeratorRequiredMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = 'blog/publication_form.html'

    def get_success_url(self):
        return reverse_lazy('blog:publication_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['multiple_photo_form'] = MultiplePhotoForm(self.request.POST, self.request.FILES)
        else:
            context['multiple_photo_form'] = MultiplePhotoForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        multiple_photo_form = context['multiple_photo_form']

        # Сохраняем публикацию
        self.object = form.save()

        # Обрабатываем фото через метод get_images формы
        if multiple_photo_form.is_valid():
            images = multiple_photo_form.get_images()
            for image in images:
                Photo.objects.create(
                    publication=self.object,
                    image=image,
                    caption=f"Фото {self.object.photos.count() + 1}"
                )

        messages.success(self.request, 'Статья успешно создана!')
        return super().form_valid(form)


class PublicationDeleteView(ModeratorRequiredMixin, DeleteView):
    model = Publication
    template_name = 'blog/publication_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('blog:publication_list')


class PublicationUpdateView(ModeratorRequiredMixin, UpdateView):
    model = Publication
    form_class = PublicationForm
    template_name = 'blog/publication_form.html'

    def get_success_url(self):
        return reverse_lazy('blog:publication_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['multiple_photo_form'] = MultiplePhotoForm(self.request.POST, self.request.FILES)
        else:
            context['multiple_photo_form'] = MultiplePhotoForm()
        context['existing_photos'] = self.object.photos.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        multiple_photo_form = context['multiple_photo_form']

        self.object = form.save()

        # Обрабатываем фото через метод get_images формы
        if multiple_photo_form.is_valid():
            images = multiple_photo_form.get_images()
            for image in images:
                Photo.objects.create(
                    publication=self.object,
                    image=image,
                    caption=f"Фото {self.object.photos.count() + 1}"
                )

        messages.success(self.request, 'Статья успешно обновлена!')
        return super().form_valid(form)


class PhotoDeleteView(ModeratorRequiredMixin, DeleteView):
    model = Photo
    template_name = 'blog/photo_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('blog:publication_update', kwargs={'pk': self.object.publication.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Фотография удалена!')
        return super().delete(request, *args, **kwargs)


def delete_photo(request, pk):
    """Функция для быстрого удаления фото"""
    photo = get_object_or_404(Photo, pk=pk)
    publication_pk = photo.publication.pk
    photo.delete()
    messages.success(request, 'Фотография удалена!')
    return redirect('blog:publication_update', pk=publication_pk)