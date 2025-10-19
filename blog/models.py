from django.contrib.postgres.indexes import GinIndex
from django.db import models

class Publication(models.Model):
    """Модель записи в блоге"""
    PUBLICATION_TYPES = [
        ('full', 'Статья для блога'),
        ('small', 'Заметка'),
    ]

    title = models.CharField(max_length=150, verbose_name='Заголовок')
    rubric = models.CharField(max_length=150, blank=True, null=True, verbose_name='Рубрика')
    text = models.TextField(verbose_name='Текст')
    preview = models.ImageField(null=True, upload_to='images/blog/preview/', verbose_name='Превью')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_published = models.BooleanField(default=True, verbose_name='Признак публикации')
    views_counter = models.IntegerField(default=0, verbose_name='Счетчик просмотров')
    publication_type = models.CharField(
        max_length=10,
        choices=PUBLICATION_TYPES,
        default='full',
        verbose_name = 'Тип статьи'
    )

    def __str__(self):
        return f'{self.title} (опубликовано {self.created_at})'

    def is_small_publication(self):
        return self.publication_type == 'small'

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'
        ordering = ['created_at', ]
        db_table = 'publications'
        indexes = [
            GinIndex(fields=['title', 'text', 'rubric']),
        ]


class Photo(models.Model):
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Статья'
    )
    image = models.ImageField(upload_to='images/blog/photos/', verbose_name='Фото')
    order = models.PositiveIntegerField(default=0, verbose_name='Номер')
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name='Подпись')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'фотография'
        verbose_name_plural = 'фотографии'
        ordering = ['order']
        db_table = 'photos'

    def save(self, *args, **kwargs):
        if not self.pk:
            # Получаем максимальный order для этой публикации и +1
            max_order = Photo.objects.filter(
                publication=self.publication
            ).aggregate(models.Max('order'))['order__max'] or 0
            self.order = max_order + 1
        super().save(*args, **kwargs)
