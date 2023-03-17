"""Модуль настройки тестов для приложения Core."""


from http import HTTPStatus

from django.test import Client, TestCase, override_settings


@override_settings(BEBUG=False)
class TestCoreAppPages(TestCase):
    """Тесты для приложения Core."""
    def setUp(self):
        """Настройка фикстур для тестов."""
        self.guest_client = Client()

    def test_404_page(self):
        """Кастоманая страница 404 использует кожидаемый шаблон."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         f'Неверный код ошибки для {HTTPStatus.NOT_FOUND}.')
        self.assertTemplateUsed(
            response,
            'core/404.html',
            msg_prefix=f'Не корректный шаблон для {HTTPStatus.NOT_FOUND}.')
