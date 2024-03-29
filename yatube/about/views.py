"""Модуль функций отображения Django."""

from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Об авторе."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Технологии."""
    template_name = 'about/tech.html'
