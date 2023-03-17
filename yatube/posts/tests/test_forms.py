"""Модуль тестов форм приложения Posts."""

import shutil
import tempfile
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings

from ..models import Comment, Group, Post
from .page_description import PageDescription

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тест формы приложения Post.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов форм приложения Posts."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUserName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа другая',
            slug='test2-slug',
            description='Тестовое описание другой группы',
        )
        cls.initial_post_text = 'Мой тестовый пост для создания.'
        cls.edited_post_text = 'Мой тестовый пост после редактирования.'
        cls.post = Post.objects.create(
            text=cls.initial_post_text,
            author=cls.user,
        )
        cls.image_for_post = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=cls.image_for_post,
            content_type='image/gif',
        )

        cls.comment_text = 'Текст комментария для тествого поста.'

        cls.pages = cls.set_post_pages_description_batch(cls)

    @classmethod
    def tearDownClass(cls) -> None:
        """Очищаем временный католаг для картинок."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        """Создаем тестовый клиент."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.initial_post_text,
            'group': self.group.pk,
            'image': self.uploaded_image,
        }
        page: PageDescription = self.pages['post_create']

        response = self.authorized_client.post(
            page.reverse_name,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            page.succses_redirect_url,
            msg_prefix='Некорректный редирект после'
                       'отправки формы создания поста.'
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=self.initial_post_text,
                group=self.group.pk,
                author=self.user,
                created__date=datetime.today(),
                image='posts/' + self.uploaded_image.name
            ).exists(),
            'Созданный пост не найден.'
        )

    def test_edit_post_text(self):
        """Валидная форма редактирования поста изменяет текст поста."""
        posts_count = Post.objects.count()
        page: PageDescription = self.pages['post_edit']
        form_data = {'text': self.edited_post_text}
        response = self.authorized_client.post(
            page.reverse_name,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response, page.succses_redirect_url,
            msg_prefix='Некорректный редирект после '
                       'отправки формы редактирования поста.'
        )

        self.assertEqual(
            Post.objects.count(), posts_count,
            'После редактирования поста, количество постов изменилось.'
        )

        post = get_object_or_404(Post, pk=self.post.pk)

        self.assertEqual(
            post.text, self.edited_post_text,
            'После редактирования, текст поста не соотвествует ожидаемому.'
        )

    def test_edit_post_group(self):
        """Валидная форма редактирования поста изменяет группу поста."""
        page: PageDescription = self.pages['post_edit']
        posts_count = Post.objects.count()
        form_data = {
            'text': self.edited_post_text,
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            page.reverse_name,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response, page.succses_redirect_url,
            msg_prefix='Некорректный редирект после '
                       'отправки формы редактирования поста.'
        )

        self.assertEqual(
            Post.objects.count(), posts_count,
            'После редактирования поста, количество постов изменилось.'
        )

        post = get_object_or_404(Post, pk=self.post.pk)
        self.assertEqual(
            post.group, self.group,
            'После редактирования, группа поста не соотвествует ожидаемой.'
        )

    def test_comment_create(self):
        """Валидная форма комментария создает комментарий."""
        page: PageDescription = self.pages['add_comment']

        comments_count = Comment.objects.count()
        form_data = {
            'text': self.comment_text,
        }
        response = self.authorized_client.post(
            page.reverse_name,
            data=form_data,
        )

        self.assertRedirects(
            response, page.succses_redirect_url,
            msg_prefix='Некорректный редирект после '
                       'отправки формы создания комментария.'
        )

        self.assertEqual(
            Comment.objects.count(), comments_count + 1,
            'После создания комментария, количество комментариев '
            'не изменилось.'
        )

        self.assertTrue(
            Comment.objects.filter(
                text=self.comment_text,
                author=self.user,
                created__date=datetime.today(),
                post=self.post,
            ).exists(),
            'Созданный комментарий не найден.'
        )
