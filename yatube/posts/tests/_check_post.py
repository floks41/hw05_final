"""Модуль функции проверки поста."""


from datetime import datetime
from typing import Optional

from ..models import Post


def check_post(self, post: Post, text: Optional[str] = None):
    """Сравнивает пост через объект на странице с тестовыми данными.

    __________
    post: Post
        пост для проверки
    text: Optional[str] = None
        необязательный аргумент текст поста для сравнения
        (используется в серийных тестах).
    """
    if text is None:
        if hasattr(self, 'post_text'):
            self.assertEqual(post.text, self.post_text,
                             'Текст поста не соотвествует ожидаемому.')
        else:
            self.assertEqual(True, False, 'Текст поста для теста не задан.')
    else:
        self.assertEqual(post.text, text,
                         'Текст поста не соотвествует ожидаемому.')

    self.assertEqual(post.author.username, self.user.username,
                     'Автор поста не соотвествует ожидаемому.')
    if post.group:
        self.assertEqual(post.group.title, self.group.title,
                         'Группа поста не соотвествует ожидаемой.')

    self.assertEqual(post.created.date(), datetime.now().date(),
                     'Дата публикации поста не соотвествует ожидаемой.')

    if post.image and hasattr(self, 'uploaded_image.name'):
        self.assertEqual(post.image, 'posts/' + self.uploaded_image.name,
                         'Картинка поста не соотвествует ожидаемой.')
