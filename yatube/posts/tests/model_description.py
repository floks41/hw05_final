"""Модуль описания моделей."""

from dataclasses import dataclass
from typing import Dict

"""@dataclass
class FieldDescription():
    """"""
    Класс описания поля модели для целей тестирования.

    Атрибуты формируются для целей серийноготестирования.
    Имя хранится в вышестоящей сущности.
    ________
    verbose_name: str
        подробное название поля
    help_text: str
        текст подсказки поля""""""
    verbose_name: str
    help_text: str"""


@dataclass
class ModelDescription():
    """Описание модели.

    Атрибуты формируются для целей серийного тестирования.
    Имя модели в сущности не хранится.
    ________
    fields: Dict[str, FieldDescription]
        словарь, ключ - имя поля модели, значение - FieldDescription
    verbose_name: str
        подробное название модели
    verbose_name_plural: str
        подробное название модели во множестенном числе
    """
    @dataclass
    class FieldDescription():
        """
        Описания поля модели для целей тестирования.

        Атрибуты формируются для целей серийного тестирования.
        Имя поля хранится в вышестоящей сущности ModelDescription.
        ________
        verbose_name: str
            подробное название поля
        help_text: str
            текст подсказки поля
        """
        verbose_name: str
        help_text: str

    fields: Dict[str, FieldDescription]
    verbose_name: str
    verbose_name_plural: str
