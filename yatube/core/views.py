"""Модуль настройки представлений приложения Core."""


from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Отображение страницы 404 NOT_FOUND."""
    return render(request, 'core/404.html', {'path': request.path},
                  status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    """Отображение страницы 403 FORBIDDEN ошибка CSRF."""
    return render(request, 'core/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request):
    """Отображение страницы 500 INTERNAL_SERVER_ERROR."""
    return render(request, 'core/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    """Отображение страницы 403 FORBIDDEN."""
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)
