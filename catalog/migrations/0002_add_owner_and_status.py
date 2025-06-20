# Generated migration for adding owner and publication_status fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0001_initial'),
    ]

    operations = [
        # Добавляем поле статуса публикации
        migrations.AddField(
            model_name='product',
            name='publication_status',
            field=models.CharField(
                choices=[
                    ('draft', 'Черновик'),
                    ('pending', 'На модерации'),
                    ('published', 'Опубликован'),
                    ('unpublished', 'Снят с публикации'),
                ],
                default='draft',
                help_text='Текущий статус публикации товара',
                max_length=20,
                verbose_name='Статус публикации'
            ),
        ),

        # Добавляем поле владельца (временно может быть NULL)
        migrations.AddField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(
                help_text='Пользователь, создавший товар',
                null=True,  # Временно разрешаем NULL
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Владелец'
            ),
        ),

        # Добавляем кастомные права доступа
        migrations.AlterModelOptions(
            name='product',
            options={
                'ordering': ['-created_at'],
                'permissions': [
                    ('can_unpublish_product', 'Может снимать товары с публикации'),
                    ('can_moderate_products', 'Может модерировать товары'),
                ],
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
            },
        ),
    ]