"""Модуль настройки приложения Admin Django."""


from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """Класс настройки админки для модели Post."""
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


admin.site.register(Post, PostAdmin)

admin.site.register(Group)
