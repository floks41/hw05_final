from typing import Dict

from .model_description import ModelDescription


def set_post_models_description_batch(self) -> Dict[str, ModelDescription]:
    """Создает описания моделей приложения Posts для целей тестирования."""
    models = {}
    models['Follow'] = ModelDescription(
        fields={
            'user': ModelDescription.FieldDescription(
                verbose_name='подписчик',
                help_text='Подписчик'
            ),
            'author': ModelDescription.FieldDescription(
                verbose_name='автор',
                help_text='Автор'
            ),
        },
        verbose_name='Подписка',
        verbose_name_plural='Подписки'
    )
    models['Group'] = ModelDescription(
        fields={
            'title': ModelDescription.FieldDescription(
                verbose_name='наименование группы',
                help_text='Введите наименование новой группы'
            ),
            'slug': ModelDescription.FieldDescription(
                verbose_name='слаг группы',
                help_text='Введите слаг новой группы'
            ),
            'description': ModelDescription.FieldDescription(
                verbose_name='описание группы',
                help_text='Введите описание новой группы'
            ),
        },
        verbose_name='Сообщество',
        verbose_name_plural='Сообщества'
    )
    models['Post'] = ModelDescription(
        fields={
            'text': ModelDescription.FieldDescription(
                verbose_name='текст поста',
                help_text='Текст нового поста'
            ),
            'author': ModelDescription.FieldDescription(
                verbose_name='автор',
                help_text='Автор поста'
            ),
            'group': ModelDescription.FieldDescription(
                verbose_name='группа',
                help_text='Группа, к которой будет относиться пост'
            ),
            'image': ModelDescription.FieldDescription(
                verbose_name='Картинка',
                help_text='Картинка к посту',
            ),
            'created': ModelDescription.FieldDescription(
                verbose_name='дата публикации',
                help_text='Дата публикации'
            ),
        },
        verbose_name='Пост',
        verbose_name_plural='Посты'
    )
    models['Comment'] = ModelDescription(
        fields={
            'text': ModelDescription.FieldDescription(
                verbose_name='текст коментария',
                help_text='Текст комментария'
            ),
            'author': ModelDescription.FieldDescription(
                verbose_name='автор',
                help_text='Автор комментария'
            ),
            'post': ModelDescription.FieldDescription(
                verbose_name='комментируемый пост',
                help_text='Пост для коментирования'
            ),
            'created': ModelDescription.FieldDescription(
                verbose_name='дата публикации',
                help_text='Дата публикации'
            ),
        },
        verbose_name='Комментарий',
        verbose_name_plural='Комментарии'
    )

    return models
