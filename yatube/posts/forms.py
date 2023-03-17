"""Модуль форм приложения Posts."""


from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    """Форма поста."""
    class Meta:
        """Класс настройки формы поста."""
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    """Форма комментария."""
    class Meta:
        """Класс настройки формы комментария."""
        model = Comment
        fields = ('text',)
