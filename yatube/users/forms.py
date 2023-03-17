"""Модуль настройки форм приложения Users."""


from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма пользователя."""
    class Meta(UserCreationForm.Meta):
        """Класс настройки форма пользователя."""
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
