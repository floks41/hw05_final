"""Модуль тестов URLS приложения Posts."""


from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Follow, Group, Post

User = get_user_model()


class TestPostURLS(TestCase):
    """Тесты URLS приложения Post.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls):
        """Настройка фикстур для тестов URLS приложения Posts."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUserName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Мой тестовый пост длиннее 15 букв'
        )
        cls.second_user = User.objects.create_user(
            username='TestSecondUserName'
        )
        cls.follow = Follow.objects.create(
            user=cls.second_user,
            author=cls.user
        )

        cls.pages = cls.set_post_pages_description_batch(cls)
        cls.unexisting_page_url = '/unexisting_page/'

    def setUp(self):
        """Создаем тестовые клиенты."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostURLS.user)
        self.authorized_second_client = Client()
        self.authorized_second_client.force_login(
            TestPostURLS.second_user
        )

    def test_urls_for_guest_are_exist(self):
        """Доступны страницы по URL для неавторизованного пользователя."""
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if not page.is_login_required:
                    response = self.guest_client.get(page.url)
                    self.assertEqual(response.status_code, HTTPStatus.OK,
                                     f'Страница {page.url} не доступна'
                                     'дла неавторизованного пользователя')

    def test_urls_for_authorizated_are_exist(self):
        """Доступны страницы по URL для авторизованного пользователя."""
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if page.is_login_required:
                    response = self.authorized_second_client.get(
                        page.url,
                        follow=True
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK,
                                     f'Страница {page.url} не доступна'
                                     'дла авторизованного пользователя')

    def test_urls_do_correct_redirect_for_guest_user(self):
        """Корректный редирект для неавторизованных пользователей.

        На страницах требующих авторизации используется
        корректный редирект для неавторизованных пользователей.
        """
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if page.is_login_required:
                    response = self.guest_client.get(page.url)
                    self.assertRedirects(
                        response,
                        page.guest_redirect_url,
                        msg_prefix=(
                            f'На странице {page.url} '
                            'редирект дла неавторизованного пользователя '
                            'не соотвествует ожидаемому.'
                        )
                    )

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соотвествующий шаблон."""
        for page in self.pages.values():
            if page.is_template_test_requred:
                with self.subTest(address=page.url):
                    response = self.authorized_client.get(page.url)
                    self.assertTemplateUsed(
                        response, page.template,
                        f'На странице {page.url} '
                        'используется шаблон не соотвествует ожидаемому.'
                    )

    def test_unexisting_page_not_found(self):
        """Несуществующая страница не найдена."""
        response = self.guest_client.get(self.unexisting_page_url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'HTTPStatus-код не существующей страницы '
                         'не соотвествует ожидаемому')
