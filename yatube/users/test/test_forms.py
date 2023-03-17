"""Настрйока тестов форм приложения Users."""


from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserFormTests(TestCase):
    """Тест формы приложения Users.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._descript_users_pages import set_users_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов форм приложения Users."""
        super().setUpClass()
        cls.pages = cls.set_users_pages_description_batch(cls)

    def setUp(self) -> None:
        """Создаем тестовый гостевой клиент."""
        super().setUp()
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пользователя.

        Форма создания пользователя формируется Django автоматически,
        поэтому типы полей не тестируем.
        """
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Пётр',
            'last_name': 'Петров оглы',
            'username': 'TestUser2',
            'email': 'address@pochta.gav',
            'password1': 'SuperablePassWord987)',
            'password2': 'SuperablePassWord987)',
        }
        page = self.pages['signup']
        response = self.guest_client.post(
            path=page.url,
            data=form_data,
            follow=True,
        )

        # Проверяем, сработал редирект успешной обработки.
        self.assertRedirects(
            response, page.succses_redirect_url,
            msg_prefix='После отправки формы регистрации '
                       'пользователя редирект не соотвествует ожидаемому.'
        )

        # Проверяем, число пользователей увеличилось на 1.
        self.assertEqual(User.objects.count(), users_count + 1,
                         'После отправки формы регистрации количество '
                         'пользователей не соотвествует ожидаемому.')

        # Проверяем, наличие пользователя с заданными значениями.
        self.assertTrue(
            User.objects.filter(
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                username=form_data['username'],
                email=form_data['email'],
            ).exists(),
            'Зарегистрированный пользователь не нейден.'
        )
