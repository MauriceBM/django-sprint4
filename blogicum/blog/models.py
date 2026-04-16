from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class TimeStampedMixin(models.Model):
    """Mixin абстрактный: добавляет поле created_at."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class PublishableMixin(TimeStampedMixin):
    """Mixin абстрактный: добавляет поле is_published."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Location(PublishableMixin):
    """Модель: географическая локация."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )

    class Meta:
        abstract = False
        ordering = ['name']
        verbose_name = 'локация'
        verbose_name_plural = 'Локации'

    def __str__(self):
        return self.name


class Category(PublishableMixin):
    """Модель: категория публикаций."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        abstract = False
        ordering = ['title']
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(PublishableMixin):
    """Модель: публикация (пост)."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Локация',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )

    class Meta:
        abstract = False
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(TimeStampedMixin):
    """Модель: комментарий к публикации."""

    text = models.TextField(
        verbose_name='Текст комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )

    class Meta:
        abstract = False
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:20]
