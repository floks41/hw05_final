"""Модуль пользовательских фильтров для шаблонов."""


from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добвляет, указанный в аргументе  CSS-класс к тегу шаблона."""
    return field.as_widget(attrs={'class': css})
