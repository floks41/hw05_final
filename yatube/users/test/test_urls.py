"""Настройка тестов URLS приложения Users."""


from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestUsersURLS(TestCase):
    """Проверка URLS приложения Users.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._descript_users_pages import set_users_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фиксутр для тестов URLS приложения Users."""
        super().setUpClass()
        cls.pages = cls.set_users_pages_description_batch(cls)
        cls.user = User.objects.create_user(username='TestUserName')

    def setUp(self):
        """Создаем тестовые клиенты."""
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=TestUsersURLS.user)

    def test_urls_for_guest_are_exist(self):
        """Доступны страницы по URL для неавторизованного пользователя."""
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if not page.is_login_required:
                    response = self.guest_client.get(page.url)
                    self.assertEqual(response.status_code, HTTPStatus.OK,
                                     f'Страница {page.url} не доступна'
                                     'дла неавторизованного пользователя')

    def test_urls_for_authorized_are_exist(self):
        """Доступны страницы по URL для авторизованного пользователя."""
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if page.is_login_required:
                    response = self.authorized_client.get(page.url)
                    self.assertEqual(response.status_code, HTTPStatus.OK,
                                     f'Страница {page.url} не доступна'
                                     'дла авторизованного пользователя')

    def test_urls_do_correct_redirect_for_guest_user(self):
        """Коорректный редирект для неавторизованных пользователей."""
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
                            'не соотвествует ожижаемому.'
                        )
                    )
