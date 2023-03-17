"""Модуль тестов моделей приложения Posts."""


from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from ..models import Group, Post
from .model_description import ModelDescription

User = get_user_model()


class PostsModelTests(TestCase):
    """Тесты моделей приложения Posts.

    Описание моделей в целях тестирования вынесено в отдельный файл.
    """
    from ._descript_post_models import set_post_models_description_batch

    @classmethod
    def setUpClass(cls):
        """Настройка фикстур для тестов моделей приложения Posts."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Мой тестовый пост длиннее 15 букв'
        )
        cls.models = cls.set_post_models_description_batch(cls)

    def check_model_fields(self, model_name: str):
        """Проверяет verbose_name и help_text полей модели."""
        model: models.Model = apps.get_model('posts', model_name)
        model_desc: ModelDescription = self.models[model_name]
        for field_name, field_desc in model_desc.fields.items():
            field = model._meta.get_field(field_name)
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    field.verbose_name,
                    field_desc.verbose_name,
                    f'Verbose_name поля {field_name} модели {model_name} '
                    'не соотвествует ожидаемому'
                )
                self.assertEqual(
                    field.help_text,
                    field_desc.help_text,
                    f'Help_text поля {field_name} модели {model_name} '
                    'не соотвествует ожидаемому'
                )

    def test_models_verbose_and_plural(self):
        """Тест Verbose_name и Verbose_name_plural моделей.

        Вызов проверки verbose_name и help_text полей модели.
        """
        for model_name, model_desc in self.models.items():
            with self.subTest(model_name=model_name):
                model = apps.get_model('posts', model_name)
                self.assertEqual(
                    model._meta.verbose_name,
                    model_desc.verbose_name,
                    f'Verbose_name модели {model_name} '
                    'не соотвествует ожидаемому'
                )
                self.assertEqual(
                    model._meta.verbose_name_plural,
                    model_desc.verbose_name_plural,
                    f'Verbose_name_plural модели {model_name} '
                    'не соотвествует ожидаемому'
                )
                self.check_model_fields(model_name)

    def test_models_have_correct__str__method(self):
        """Проверяем, что у моделей корректно работает метод __str__."""
        self.assertEqual(
            self.post.__str__(),
            'Мой тестовый по',
            'Неверно работает метод __str__ модели Post'
        )
        self.assertEqual(
            self.group.__str__(),
            'Тестовая группа',
            'Неверно работает метод __str__ модели Group'
        )
