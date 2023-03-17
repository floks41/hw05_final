"""Создание описаний страниц приложения Users для целей тестирования."""


from typing import Dict

from django.contrib.auth import get_user_model
from django.urls import reverse

from .page_description import PageDescription

User = get_user_model()


def set_users_pages_description_batch(self) -> Dict[str, PageDescription]:
    """Создает описания страниц приложения Users для целей тестирования."""
    pages = {}
    pages['signup'] = PageDescription(
        url='/auth/signup/',
        template='users/signup.html',
        reverse_name=reverse('users:signup'),
        succses_redirect_url=reverse('posts:index'),
    )

    pages['login'] = PageDescription(
        url='/auth/login/',
        template='users/login.html',
        reverse_name=reverse('users:login')
    )

    pages['logout'] = PageDescription(
        url='/auth/logout/',
        template='users/logged_out.html',
        reverse_name=reverse('users:logout'),
    )

    pages['password_change_form'] = PageDescription(
        url='/auth/password_change/',
        template='users/password_change_form.html',
        is_template_test_requred=False,
        is_login_required=True,
        guest_redirect_url='/auth/login/?next=/auth/password_change/',
        reverse_name=reverse('users:password_change_form')
    )
    """Механизм работы django.contrib.auth.auth_views.PasswordChangeView
    исключает тест шаблоны применяемыми средствами.
    """

    pages['password_change_done'] = PageDescription(
        url='/auth/password_change/done/',
        template='users/password_change_done.html',
        is_template_test_requred=False,
        is_login_required=True,
        guest_redirect_url='/auth/login/?next=/auth/password_change/done/',
        reverse_name=reverse('users:password_change_done')
    )
    """Механизм работы django.contrib.auth.auth_views.PasswordChangeDoneView
    исключает тест шаблоны применяемыми средствами.
    """

    pages['password_reset_form'] = PageDescription(
        url='/auth/password_reset/',
        template='users/password_reset_form.html',
        reverse_name=reverse('users:password_reset_form')
    )

    pages['password_reset_done'] = PageDescription(
        url='/auth/password_reset/done/',
        template='users/password_reset_done.html',
        reverse_name=reverse('users:password_reset_done')
    )

    pages['password_reset_complite'] = PageDescription(
        url='/auth/reset/done/',
        template='users/password_reset_complete.html',
        reverse_name=reverse('users:password_reset_complite')
    )
    pages['password_reset_confirm'] = PageDescription(
        url='/auth/reset/<uidb64>/<token>/',
        template='users/password_reset_confirm.html',
        reverse_name=reverse(
            'users:password_reset_confirm',
            kwargs={'uidb64': '1', 'token': '1'}
        )
    )

    return pages
