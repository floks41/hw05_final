"""Модуль настройки моделей Django."""


from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DateTimedModel(models.Model):
    """Абстрактная модель с полем created (тип model.DateTimeField)."""
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
        help_text='Дата публикации'
    )

    class Meta:
        """Мета опции абстрактной модели DateTimedModel."""
        abstract = True
        ordering = ('-created',)


class Group(models.Model):
    """Сообщества."""
    title = models.CharField(
        max_length=200,
        verbose_name='наименование группы',
        help_text='Введите наименование новой группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='слаг группы',
        help_text='Введите слаг новой группы',
    )
    description = models.TextField(
        verbose_name='описание группы',
        help_text='Введите описание новой группы',
    )

    class Meta:
        """Мета опции модели Group."""
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self) -> str:
        """Отображениние информации об объекте класса Group."""
        return self.title


class Post(DateTimedModel):
    """Запись."""
    text = models.TextField(
        verbose_name='текст поста',
        help_text='Текст нового поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        help_text='Картинка к посту',
        blank=True
    )

    class Meta(DateTimedModel.Meta):
        """Мета опции модели Post."""
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        """Выводим текст поста."""
        return self.text[:15]


class Comment(DateTimedModel):
    """Комментарий."""
    text = models.TextField(
        verbose_name='текст коментария',
        help_text='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
        help_text='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментируемый пост',
        help_text='Пост для коментирования'
    )

    class Meta(DateTimedModel.Meta):
        """Мета опции модели comment."""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """Выводим текст комментария."""
        return self.text[:15]


class Follow(models.Model):
    """Подписка на авторов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
        help_text='Автор'
    )

    class Meta:
        """Мета опции модели follow."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            ),

            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='users_cannot_follow_themselves',
            )
        ]
