"""Модуль тестов представлений приложения Posts."""


import shutil
import tempfile
from time import sleep

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings

from ..models import Comment, Follow, Group, Post
from .page_description import PageDescription

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesSerialTests(TestCase):
    """Тест страниц приложения Post. Серийные тесты и тесты паджинатора.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._check_post import check_post
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов представления приложения Posts.

        Для серийных тестов и тестов паджинатора создаются тестовые записи
        Post в количестве большем на NUMBER_OF_POSTS_FOR_SECOND_PAGE,
        чем выводит на страницу paginator.
        Все записи от одного пользователя и одной группы.
        Создание описаний страниц приложения Users для целей тестирования
        вынесено в отдельный файл.
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUserName')
        cls.second_user = User.objects.create_user(
            username='TestSecondUserName')
        cls.follow = Follow.objects.create(
            user=cls.second_user, author=cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.NUMBER_OF_POSTS_FOR_SECOND_PAGE = 3
        cls.posts_count = (
            settings.NUMBER_OF_POSTS_TO_VIEW
            + cls.NUMBER_OF_POSTS_FOR_SECOND_PAGE
        )
        for i in range(cls.posts_count):
            Post.objects.create(
                author=cls.user,
                text=f'Мой тестовый пост номер {i+1}.',
                group=cls.group
            )
            # Делаем паузу, чтобы дата публикации соотносилась с PK.
            sleep(0.00001)
        cls.first_post_text = 'Мой тестовый пост номер 1.'
        cls.last_post_text = f'Мой тестовый пост номер {cls.posts_count}.'

        cls.pages = cls.set_post_pages_description_batch(cls)

    def setUp(self) -> None:
        """Создаем тестовый клиент для тестов."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            PostPagesSerialTests.user)

        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(
            PostPagesSerialTests.second_user)

    def test_pages_use_correct_templates(self):
        """Страницы по namespace:name используют соотвествующий шаблон."""
        for page in self.pages.values():
            if page.is_template_test_requred:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.authorized_client.get(
                        page.reverse_name
                    )
                    self.assertTemplateUsed(
                        response,
                        page.template,
                        f'Страница {page.reverse_name} использует неверный '
                        'шаблон.'
                    )

    def test_paginators_first_pages(self):
        """Тест первой страницы паджинатора. Количество записей.

        Паджинатор на первой странице выдает ожидаемое
        количество записей.
        """
        for page in self.pages.values():
            if page.has_paginator:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.second_authorized_client.get(
                        page.reverse_name)
                    self.assertIsInstance(
                        response.context[page.paginator_object_name],
                        Page,
                        f'На странице {page.reverse_name} '
                        'не найден объект паджинатора.'
                    )
                    self.assertEqual(
                        len(response.context[page.paginator_object_name]),
                        settings.NUMBER_OF_POSTS_TO_VIEW,
                        f'На первой странице {page.reverse_name} паджинатор'
                        'выдает неверное количество записей.'
                    )

    def test_paginators_second_pages(self):
        """Тест второй страницы паджинатора. Количество записей.

        Пагинатор на второй странице выдает ожидаемое количество записей.
        """
        for page in self.pages.values():
            if page.has_paginator:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.second_authorized_client.get(
                        page.second_page_reverse_name
                    )
                    self.assertIsInstance(
                        response.context[page.paginator_object_name],
                        Page,
                        f'На странице {page.second_page_reverse_name} '
                        'не найден объект паджинатора.'
                    )
                    self.assertEqual(
                        len(response.context[page.paginator_object_name]),
                        self.NUMBER_OF_POSTS_FOR_SECOND_PAGE,
                        f'На странице {page.second_page_reverse_name} '
                        'паджинатор выдает неверное количество записей.'
                    )

    def test_paginators_first_post_on_first_page(self):
        """Тест паджинатора. Первая запись.

        Содержимое первой записи на страницах с паджинатором
        соответствует ожидаемому.
        """
        for page in self.pages.values():
            if page.has_paginator:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.second_authorized_client.get(
                        page.reverse_name)
                    # Получаем содержимое первой записи на странице
                    first_object = response.context[
                        page.paginator_object_name
                    ][0]
                    # Проверяем содержимое первой записи на странице
                    self.check_post(
                        post=first_object,
                        text=self.last_post_text
                    )

    def test_paginators_last_post_on_second_page(self):
        """Вторая страница паджинатора. Последняя запись.

        Содержимое последней записи на вторых страницах
        с паджинатором соответствует ожидаемому.
        """
        for page in self.pages.values():
            if page.has_paginator:
                with self.subTest(reverse_name=page.reverse_name):

                    response = self.second_authorized_client.get(
                        page.second_page_reverse_name
                    )

                    last_object = response.context[
                        page.paginator_object_name
                    ][self.NUMBER_OF_POSTS_FOR_SECOND_PAGE - 1]

                    self.check_post(
                        post=last_object,
                        text=self.first_post_text
                    )

    def test_paginators_pages_context_have_correct_objects(self):
        """В контектсе страниц корректные объекты.

        Имена и типы объектов в контексте страниц
        соответствуют ожидаемым.
        """
        for page in self.pages.values():
            if page.has_paginator:
                with self.subTest(reverse_name=page.reverse_name):
                    response = self.second_authorized_client.get(
                        page.reverse_name)
                    if page.has_additional_objects:
                        for object_name, expected_type in (
                            page.additional_objects.items()
                        ):
                            self.assertTrue(
                                object_name in response.context,
                                f'В контексте страницы {page.reverse_name} '
                                f'неверный объект {object_name}.'
                            )

                            self.assertIsInstance(
                                response.context[object_name],
                                expected_type,
                                f'В контексте страницы {page.reverse_name} '
                                f'объект {object_name} неверного типа.'
                            )

    def test_forms_have_correct_fields_types(self):
        """Типы полей формы соотвествуют ожидаемым, на страницах с формами."""
        for page in self.pages.values():
            if page.has_form:
                response = self.authorized_client.get(page.reverse_name)
                for value, expected in page.form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            page.form_object_name
                        ).fields.get(value)
                        self.assertIsInstance(
                            form_field, expected,
                            f'В форме страницы {page.reverse_name} поле'
                            f'{form_field} не соответствует типу {expected}.'
                        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesIndividualTests(TestCase):
    """Тест страниц приложения Post. Единичные тесты.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._check_post import check_post
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser1Name')
        cls.second_user = User.objects.create_user(username='TestUser2Name')

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

        cls.post_text = 'Мой тестовый пост.'

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

        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text,
            group=cls.group,
            image='posts/' + cls.uploaded_image.name
        )

        cls.comment_text = 'Текст комментария для тествого поста.'

        cls.comment = Comment.objects.create(
            text=cls.comment_text,
            author=cls.user,
            post=cls.post
        )

        cls.pages = cls.set_post_pages_description_batch(cls)

    @classmethod
    def tearDownClass(cls) -> None:
        """Очищаем временный католаг для картинок."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        """Создаем тестовый клиент, пользователь - автор поста."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesIndividualTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом. pk=1."""
        page: PageDescription = self.pages['post_detail']
        response = self.authorized_client.get(page.reverse_name)

        first_object = response.context['post']

        self.check_post(first_object)

        self.assertLessEqual(
            len(response.context['short_text_of_post']),
            settings.NUMBER_OF_SYMBOLS_TO_VIEW,
            f'Короткий текст поста на странице {page.reverse_name} '
            'не соответствует ожидаемому.'
        )

    def test_post_edit_page_show_correct_context(self):
        """Шаблон страницы post_edit сформирован с правильным контекстом.

        Тест для записи с pk=1. Проверяем значение is_edit==True,
        заполнение полей на форме редактирования.
        """
        page: PageDescription = self.pages['post_edit']
        response = self.authorized_client.get(page.reverse_name)
        self.assertTrue(response.context['is_edit'],
                        'Значение переменной is_edit на странице '
                        f'{page.reverse_name} не соответствует ожидаемому.')
        form = response.context[page.form_object_name]
        self.assertEqual(form.initial.get('text'), self.post_text,
                         f'Текст поста на странице {page.reverse_name} '
                         'не соответствует ожидаемому.')
        self.assertEqual(form.initial.get('group'), self.group.pk,
                         f'Группа поста на странице {page.reverse_name} '
                         'не соответствует ожидаемой.')
        self.assertEqual(
            form.initial.get('image'),
            'posts/' + self.uploaded_image.name,
            f'Картинка posts/{self.uploaded_image.name} '
            'не соотвествует картинке выбранной в форме'
        )

    def test_post_create_page_show_correct_context(self):
        """Шаблон страницы post_create сформирован с правильным контекстом."""
        page: PageDescription = self.pages.get('post_create')
        response = self.authorized_client.get(page.reverse_name)
        self.assertFalse(response.context['is_edit'],
                         'Значение переменной is_edit на странице '
                         f'{page.reverse_name} не соответствует ожидаемому.')

    def test_post_is_displayed_in_its_author_profile(self):
        """Тестовый пост отображается в профиле автора."""
        page: PageDescription = self.pages['profile']
        response = self.authorized_client.get(page.reverse_name)
        first_object = response.context[page.paginator_object_name][0]
        self.assertEqual(len(response.context[page.paginator_object_name]), 1,
                         'Количество записей в профиле автора '
                         'не соотвествует ожидаемому.')
        self.check_post(first_object)

    def test_post_is_not_displayed_in_another_user_profile(self):
        """Тестовый пост не отображается в профиле другого пользователя."""
        page: PageDescription = self.pages['profile']
        response = self.authorized_client.get(page.reverse_second)
        self.assertEqual(len(response.context[page.paginator_object_name]), 0,
                         'Количество записей в профиле другого пользователя '
                         'не соотвествует ожидаемому.')

    def test_post_is_displayed_in_group_list(self):
        """Тестовый пост отображается на странице группы к которой отнесен."""
        page: PageDescription = self.pages['group_list']
        response = self.authorized_client.get(page.reverse_name)
        first_object = response.context[page.paginator_object_name][0]
        self.assertEqual(len(response.context[page.paginator_object_name]), 1,
                         'Количество записей на странице группы '
                         'не соотвествует ожидаемому.')
        self.check_post(first_object)

    def test_post_is_not_displayed_in_another_group_list(self):
        """Тестовый пост не отображается на странице другой группы."""
        page: PageDescription = self.pages['group_list']
        response = self.authorized_client.get(page.reverse_second)
        self.assertEqual(len(response.context[page.paginator_object_name]), 0,
                         'Количество записей на странице другой группы '
                         'не соотвествует ожидаемому.')

    def test_post_is_displayed_in_index_page(self):
        """Тестовый пост отображается на главной странице проекта."""
        page: PageDescription = self.pages['index']
        response = self.authorized_client.get(page.reverse_name)
        first_object = response.context[page.paginator_object_name][0]
        self.assertEqual(len(response.context[page.paginator_object_name]), 1,
                         'Количество записей на главной странице '
                         'не соотвествует ожидаемому.')
        self.check_post(first_object)

    def test_comment_is_displayed_in_post_detail(self):
        """Тестовый комментарий отображается на странице поста."""
        page: PageDescription = self.pages['post_detail']
        response = self.authorized_client.get(page.reverse_name)
        post = response.context['post']
        self.assertEqual(post.comments.count(), 1, 'Количество '
                         'комментариев не соотвествует ожидаемому')
        comment = post.comments.all()[:1][0]
        self.assertEqual(comment.text, self.comment_text, 'Текст созданного '
                         'комментария не соотвествует ожидаемому.')


class PostPagesCacheTest(TestCase):
    """Тест работы кэша страниц приложения Post.

    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._check_post import check_post
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser1Name')
        cls.second_user = User.objects.create_user(username='TestUser2Name')

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

        cls.post_text = 'Мой первый тестовый пост, его оставим.'
        cls.second_post_text = 'Второй пост, совсем другой, его удалим.'

        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text,
            group=cls.group,
        )

        cls.second_post = Post.objects.create(
            author=cls.second_user,
            text=cls.second_post_text,
            group=cls.second_group,
        )

        cls.pages = cls.set_post_pages_description_batch(cls)

        cache.delete('index_page')

    def setUp(self) -> None:
        """Создаем тестовый клиент, пользователь - автор поста."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesCacheTest.user)

    def test_index_page_cache_works(self):
        """Тест кеширования главной страницы.

        Тестовый пост после удаления, остается на главной странице
        до принудительной очистки кеша.
        """
        page: PageDescription = self.pages['index']
        posts_count = Post.objects.count()
        initial_response = self.authorized_client.get(page.reverse_name)
        self.assertEqual(
            len(initial_response.context[page.paginator_object_name]),
            posts_count,
            'Количество записей на главной странице '
            'не соотвествует ожидаемому перед удалением поста.'
        )

        self.second_post.delete()

        after_post_delete_response = self.authorized_client.get(
            page.reverse_name)

        self.assertEqual(
            initial_response.content,
            after_post_delete_response.content,
            'Контент главной страницы изменился'
            'после удаления поста перед очисткой кэша.')

        cache.delete('index_page')

        response = self.authorized_client.get(page.reverse_name)
        self.assertEqual(
            len(response.context[page.paginator_object_name]),
            posts_count - 1,
            'Количество записей на главной странице '
            'не соотвествует ожидаемому после удаления поста'
            'и очистки кэша index_page.'
        )

        first_object = response.context[page.paginator_object_name][0]

        self.check_post(first_object)


class FollowUnfollowTest(TestCase):
    """Тест создания и удаления подписки Follow.

    Авторизованный пользователь может подписываться
    на других пользователей и удалять их из подписок.
    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._check_post import check_post
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов."""
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser1Name')
        cls.second_user = User.objects.create_user(username='TestUser2Name')

        cls.post_text = 'Тестовый пост от автора, на которого будет подписка.'

        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text,
        )

        cls.pages = cls.set_post_pages_description_batch(cls)

        cache.delete('index_page')

    def setUp(self) -> None:
        """Создаем тестовый клиент, пользователь - автор поста."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowUnfollowTest.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(
            FollowUnfollowTest.second_user)

    def test_profile_follow_and_unfollow(self):
        """Авторизованный пользователь может подписаться на другого автора.

        И отписаться от него.
        """
        follow_index: PageDescription = self.pages['follow_index']
        response = self.second_authorized_client.get(
            follow_index.reverse_name)
        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'У пользователя без подписок на странице подписок не пусто.'
        )
        profile_follow: PageDescription = self.pages['profile_follow']
        response = self.second_authorized_client.get(
            profile_follow.reverse_name)

        self.assertEqual(
            Follow.objects.filter(
                user=self.second_user, author=self.user
            ).count(), 1,
            'Количество подписок второго пользователя на первого автора '
            'не соотвествует ожидаемому (после создания подписки).'
        )

        response = self.second_authorized_client.get(
            follow_index.reverse_name)
        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 1,
            'Количество постов на странице подписок пользователя '
            'не соотвествует ожидаемому.'
        )

        post = response.context[follow_index.paginator_object_name][0]
        self.check_post(post)

        profile_unfollow: PageDescription = self.pages['profile_unfollow']
        response = self.second_authorized_client.get(
            profile_unfollow.reverse_name)

        self.assertEqual(
            Follow.objects.filter(
                user=self.second_user, author=self.user
            ).count(), 0,
            'Количество подписок второго пользователя на первого автора '
            'не соотвествует ожидаемому (после удаления подписки).'
        )

        response = self.second_authorized_client.get(
            follow_index.reverse_name)
        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'Количество постов на странице подписок пользователя '
            'не соотвествует ожидаемому после удаления подписки.'
        )


class FollowingPosts(TestCase):
    """Тест создания поста в подписке.

    Новая запись пользователя появляется в ленте тех,
    кто на него подписан и не появляется в ленте тех, кто не подписан.
    Создание описаний страниц приложения для целей тестирования
    вынесено в отдельный файл.
    """
    from ._check_post import check_post
    from ._descript_post_pages import set_post_pages_description_batch

    @classmethod
    def setUpClass(cls) -> None:
        """Настройка фикстур для тестов."""
        super().setUpClass()

        # Автор
        cls.user = User.objects.create_user(username='TestUser1Name')
        # Подписчик
        cls.second_user = User.objects.create_user(username='TestUser2Name')
        # Подписчик другой
        cls.third_user = User.objects.create_user(username='TestUser3Name')
        Follow.objects.create(
            user=cls.second_user, author=cls.user)
        Follow.objects.create(
            user=cls.third_user, author=cls.second_user)

        cls.post_text = 'Тестовый пост от автора, на которого будет подписка.'

        cls.pages = cls.set_post_pages_description_batch(cls)

        cache.delete('index_page')

    def setUp(self) -> None:
        """Создаем тестовые клиенты."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowingPosts.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(
            FollowingPosts.second_user)
        self.third_authorized_client = Client()
        self.third_authorized_client.force_login(
            FollowingPosts.third_user)

    def test_follow_post_is_displayed_correct(self):
        """Пост автора корректно отображается на странице подписчика.

        И не отображается в лентах других пользователей.
        """
        follow_index: PageDescription = self.pages['follow_index']
        response = self.second_authorized_client.get(
            follow_index.reverse_name)
        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'У пользователя на странице подписок не пусто,'
            'но автор, на которого подписан пользователь, не создавал постов.'
        )

        self.post = Post.objects.create(
            author=self.user,
            text=self.post_text,
        )

        response = self.second_authorized_client.get(
            follow_index.reverse_name)

        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 1,
            'Количество постов в ленте пользователя не соотвествует '
            'ожидаемому,после того как автор, на которого подписан '
            'пользователь, создал пост.'
        )

        post = response.context[follow_index.paginator_object_name][0]
        self.check_post(post)

        response = self.authorized_client.get(
            follow_index.reverse_name)

        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'У автора поста, который не имеет подписок, на странице '
            'подписок не пусто.'
        )

        response = self.third_authorized_client.get(
            follow_index.reverse_name)

        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'У другого подписчика, для которого нет постов, на странице '
            'подписок не пусто.'
        )

        post.delete()

        response = self.second_authorized_client.get(
            follow_index.reverse_name)

        self.assertEqual(
            len(response.context[follow_index.paginator_object_name]), 0,
            'У пользователя на странице подписок не пусто, '
            'но пост автора, на которого подписан пользователь, удален.'
        )
