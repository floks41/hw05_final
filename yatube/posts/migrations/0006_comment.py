# Generated by Django 2.2.16 on 2023-03-14 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0005_auto_20230314_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст комментария', verbose_name='текст коментария')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата создания комментария', verbose_name='дата комментария')),
                ('author', models.ForeignKey(help_text='Автор комментария', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('post', models.ForeignKey(help_text='Пост для коментирования', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='комментируемый пост')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-created',),
            },
        ),
    ]
