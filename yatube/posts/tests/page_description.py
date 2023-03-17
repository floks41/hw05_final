"""Модель класса описания страниц приложения для целей тестирования."""


from dataclasses import dataclass
from typing import Optional


@dataclass
class PageDescription():
    """
    Класс описания страницы для целей тестирования.

    Атрибуты формируются для целей серийного и единичного тестирования.
    ________
    url: str
        url страницы из urls.py
    reverse_name: str
        Результат работы reverse(namespece:name) из urls.py
        аргументы подставлются при создании экземпляра класса,
        как правило - первой записи.
    template: str
        Адрес шаблона, используемого при формировании страницы
    is_login_required: bool = False
        Страница только для авторизованных пользователей,
        значение по умолчанию False.
    is_template_test_requred: bool = True
        Использование шаблона, подлежит тестированию,
        значение по умолчанию True,
        используется для исключения тестирования шаблонов страниц,
        формируемых встроенными view-функциями Django,
        исключающими тест шаблона.
    guest_redirect_url: Optional[str] = None
        Адрес для редиректа неавторизованных пользователей.
    succses_redirect_url: Optional[str] = None
        адрес редиректа при успешной обработке валидной формы
    reverse_last: Optional[str] = None
        результат работы reverse(namespece:name) из urls.py
        аргументы подставлются при создании экземпляра класса,
        как правило - указывают на последнюю созданную запись
    reverse_second: Optional[str] = None
        Результат работы reverse(namespece:name) из urls.py
        аргументы подставлются при создании экземпляра класса,
        как правило - указывают на вторую созданную запись.
        (используется для серийных тестов и тестов паджинатора)
    has_additional_objects: bool = False
        Контект страницы имеет дополнительные объекты.
    additional_objects: Optional[dict[str, object]] = None
        Словарь дополнительных объектов контекста,
        за исключение объекта паджинатора, объект формы включается,
        ключ - имя, значение - тип.
    has_form: bool = False
        В контекстве страницы имеется форма. Значение по умолчению False.
    form_object_name: str = 'form'
        Имя объекта формы в контексте страницы. Значение по умолчению 'form'.
    form_fields: Optional[dict[str, object]] = None
        Словарь полей формы, ключ - имя, значение - тип.
    has_paginator: bool = False
        Страница имеет объект паджинатора по конткесте.
    paginator_object_name: str = 'page_obj'
        Имя объекта паджинатора в контексте страницы.
    Свойство
    ________
    second_page_reverse_name: str = self.reverse_name + '?page=2'
        Результат работы reverse(namespece:name) из urls.py
        с указанием на вторую страницу. Используется для тестов паджинатора.
    """
    url: str
    reverse_name: str
    # template: Optional[str] = None
    is_login_required: bool = False
    is_template_test_requred: bool = True
    template: Optional[str] = None
    guest_redirect_url: Optional[str] = None
    succses_redirect_url: Optional[str] = None
    reverse_last: Optional[str] = None
    reverse_second: Optional[str] = None
    has_additional_objects: bool = False
    additional_objects: Optional[dict[str, object]] = None
    has_form: bool = False
    form_object_name: str = 'form'
    form_fields: Optional[dict[str, object]] = None
    has_paginator: bool = False
    paginator_object_name: str = 'page_obj'

    def __post_init__(self):
        """Дополнительные атрибуты."""
        if self.reverse_name:
            self.second_page_reverse_name: str = self.reverse_name + '?page=2'
