"""Модуль настройки тестов для приложения About."""
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class TestAboutAppPages(TestCase):
    """Тесты для приложения About."""
    def setUp(self):
        """Настройка фикстур для тестов."""
        self.guest_client = Client()
        self.urls_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        self.pages_templates_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

    def test_url_uses_correct_templates(self):
        """URL-адрес использует соотвествующий шаблон."""
        for address, template in self.urls_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'Используется не верный шаблон.')

    def test_url_exists_at_desired_locations_for_guest_client(self):
        """Существуют страницы для не авторизованного поользователя."""
        for address in self.urls_templates_names.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Страница недоступна для неавторизованного пользователя.'
                )

    def test_page_exists_at_desired_locations_for_guest_clie(self):
        """Cтраница по namespace:name существует.

        Для не авторизованного пользователя.
        """
        for reverse_name, template in self.pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Страница недоступна для авторизованного пользователя.'
                )

    def test_pages_uses_correct_templates(self):
        """Страница по namespace:name использует соотвествующий шаблон."""
        for reverse_name, template in self.pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Используется не корректный шаблон.'
                )
