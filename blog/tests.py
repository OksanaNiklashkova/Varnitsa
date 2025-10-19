import tempfile
from io import BytesIO
from PIL import Image
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Publication, Photo
from users.models import User


class BlogTestBase(TestCase):
    """Базовый класс для тестов блога"""

    def setUp(self):
        # создаем тестового авторизованного пользователя
        self.moderator = User.objects.create_user(
            username='moderator',
            password='modpass123',
            email='moderator@example.com'
        )

        # Создаем тестовые публикации БЕЗ изображений
        self.publication1 = Publication.objects.create(
            title='Новое пиво',
            text='Текст о новом пиве',
            rubric='Новости',
            publication_type='full',
            is_published=True
        )

        self.publication2 = Publication.objects.create(
            title='Новый лимонад',
            text='Текст о новом лимонаде',
            rubric='Новости',
            publication_type='full',
            is_published=True
        )

        self.publication3 = Publication.objects.create(
            title='Новаторские технологии',
            text='Текст о новаторских',
            rubric='Новости',
            publication_type='small',
            is_published=True
        )

        # Создаем тестовые фото с минимальными файлами
        self.photo1 = Photo.objects.create(
            publication=self.publication2,
            image=SimpleUploadedFile(
                name='test_photo1.jpg',
                content=b'',
                content_type='image/jpeg'
            ),
            caption='Фото 1'
        )

        self.photo2 = Photo.objects.create(
            publication=self.publication2,
            image=SimpleUploadedFile(
                name='test_photo2.jpg',
                content=b'',
                content_type='image/jpeg'
            ),
            caption='Фото 2'
        )

        self.client = Client()

    def set_age_verified(self):
        """Устанавливает возрастную проверку в сессии"""
        session = self.client.session
        session['age_verified'] = True
        session.save()

    def login_as_moderator(self):
        """Логинит модератора и устанавливает возрастную проверку"""
        self.client.force_login(self.moderator)
        self.set_age_verified()
        return True

class PublicationListViewTests(BlogTestBase):
    """ Тесты для контроллера отображения списка статей """
    def test_publications_list_view_success(self):
        """ Тест успешного формирования списка всех статей """
        self.set_age_verified()
        response = self.client.get(reverse('blog:publication_list'))
        publications = response.context['publications']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/publication_list.html')
        self.assertIn('publications', response.context)
        self.assertEqual(publications.count(), 2)
        self.assertTrue(all(publication.is_published for publication in publications))


class SmallPublicationListViewTests(BlogTestBase):
    """ Тесты для контроллера отображения списка инфо-заметок """
    def test_small_publications_list_view_success(self):
        """ Тест успешного формирования списка инфо-заметок """
        self.set_age_verified()
        response = self.client.get(reverse('blog:info_list'))
        publications = response.context['publications']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/small_publication_list.html')
        self.assertIn('publications', response.context)
        self.assertEqual(publications.count(), 1)
        self.assertTrue(all(publication.is_published for publication in publications))


class PublicationDetailViewTests(BlogTestBase):
    """ Тесты для контроллера отображения отдельной статьи """
    def test_publication_detail_view_success(self):
        """ Тест успешного формирования страницы с отображением статьи """
        self.set_age_verified()
        self.publication = Publication.objects.get(title='Новое пиво')
        count_views = self.publication.views_counter
        url = reverse('blog:publication_detail', kwargs={'pk': self.publication.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/publication_detail.html')
        self.assertEqual(response.context['publication'], self.publication)
        self.assertIn('publication', response.context)
        refresh_publication = Publication.objects.get(title='Новое пиво')
        self.assertEqual(count_views + 1, refresh_publication.views_counter)


class PublicationCreateViewTests(BlogTestBase):
    """Тесты для контроллера создания публикации"""

    def test_publication_create_success(self):
        """Тест успешного создания статьи для блога"""
        self.login_as_moderator()

        form_data = {
            'title': 'Новости о нас',
            'text': 'Текст о выставке',
            'rubric': 'Новости',
            'publication_type': 'full',
            'is_published': True
        }

        response = self.client.post(
            reverse('blog:publication_create'),
            data=form_data
        )

        self.assertTrue(Publication.objects.filter(title='Новости о нас').exists())
        new_publication = Publication.objects.get(title='Новости о нас')
        expected_url = reverse('blog:publication_detail', kwargs={'pk': new_publication.pk})
        self.assertRedirects(response, expected_url)


class PublicationUpdateViewTests(BlogTestBase):
    """Тесты для контроллера изменения публикации"""

    def test_publication_update_success(self):
        """Тест успешного изменения статьи для блога"""
        self.login_as_moderator()
        publication = Publication.objects.get(title='Новое пиво')
        url = reverse('blog:publication_update', kwargs={'pk': publication.pk})

        form_data = {
            'title': 'Обновленное пиво',
            'text': 'Обновленный текст о выставке',
            'rubric': 'Новости',
            'publication_type': 'full',
            'is_published': True
        }

        response = self.client.post(url, data=form_data)

        # Проверяем редирект на страницу деталей публикации
        expected_url = reverse('blog:publication_detail', kwargs={'pk': publication.pk})
        self.assertRedirects(response, expected_url)

        # Проверяем что статья изменилась
        updated_publication = Publication.objects.get(pk=publication.pk)
        self.assertEqual(updated_publication.title, 'Обновленное пиво')
        self.assertEqual(updated_publication.text, 'Обновленный текст о выставке')


class PublicationDeleteViewTests(BlogTestBase):
    """ Тесты для контроллера удаления статьи """
    def test_publication_delete_view_success(self):
        """ Тесты успешного удаления публикации """
        self.login_as_moderator()
        self.publication = Publication.objects.get(title='Новый лимонад')
        url = reverse('blog:publication_delete', kwargs={'pk': self.publication.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('blog:publication_list'))
        self.assertFalse(Publication.objects.filter(pk=self.publication.pk).exists())


class PhotoDeleteViewTests(BlogTestBase):
    """Тесты для контроллера удаления фото (CBV)"""

    def test_photo_delete_view_post_success(self):
        """Тест успешного удаления фото через POST"""
        self.login_as_moderator()
        url = reverse('blog:photo_delete', kwargs={'pk': self.photo1.pk})

        # Получаем объект фото для проверки publication_pk
        photo_obj = Photo.objects.get(pk=self.photo1.pk)
        publication_pk = photo_obj.publication.pk

        # Проверяем что фото существует до удаления
        self.assertTrue(Photo.objects.filter(pk=self.photo1.pk).exists())

        response = self.client.post(url)

        # Проверяем редирект БЕЗ автоматического следования
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('blog:publication_update', kwargs={'pk': publication_pk})
        self.assertEqual(response.url, expected_url)

        # Проверяем что фото удалено
        self.assertFalse(Photo.objects.filter(pk=self.photo1.pk).exists())
