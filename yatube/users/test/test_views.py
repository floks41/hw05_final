"""Настройка тестов работы представлений приложения Users."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestUsersViews(TestCase):
    """Проверка views приложения Users.

    Создание описаний страниц приложения Users для целей тестирования
    вынесено в отдельный файл.
    """
    from ._descript_users_pages import set_users_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов представлений приложения Users."""
        super().setUpClass()
        cls.pages = cls.set_users_pages_description_batch(cls)
        cls.user = User.objects.create_user(username='TestUserName')

    def setUp(self):
        """Клиенты для тестов представлений приложения Users."""
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.login(user=TestUsersViews.user)

    def test_pages_use_correct_templates(self):
        """Страницы по namespace:name использует соотвествующий шаблон."""
        for page in self.pages.values():
            if page.is_template_test_requred:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.authorized_client.get(page.reverse_name)
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                        f'Страница {page.reverse_name} не доступна.'
                    )
                    self.assertTemplateUsed(
                        response,
                        page.template,
                        f'Страница {page.reverse_name} '
                        'использует неверный шаблон.'
                    )

    def test_path_name_for_guest_are_exist(self):
        """Доступны страницы по namespace:name.

        Для неавторизованного пользователя.
        """
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if not page.is_login_required:
                    response = self.guest_client.get(page.reverse_name)
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                        f'Страница {page.reverse_name} не доступна.'
                    )

    def test_path_for_authorizted_are_exist(self):
        """Доступны страницы по namespace:name.

        Для авторизованного пользователя.
        """
        for page in self.pages.values():
            with self.subTest(address=page.url):
                if page.is_login_required:
                    response = self.authorized_client.get(
                        page.reverse_name,
                        follow=True
                    )
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                        f'Страница {page.reverse_name} не доступна.'
                    )
