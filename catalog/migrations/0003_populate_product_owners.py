# Generated migration for populating owner field and making it required

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_product_owners(apps, schema_editor):
    """
    Заполняем поле owner для существующих товаров.
    Назначаем первого суперпользователя владельцем всех товаров.
    """
    Product = apps.get_model('catalog', 'Product')
    User = apps.get_model(settings.AUTH_USER_MODEL)

    # Ищем первого суперпользователя
    try:
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            # Если нет суперпользователей, создаем временного пользователя
            superuser = User.objects.create_user(
                username='temp_owner',
                email='temp@example.com',
                is_staff=True,
                is_superuser=True
            )
            print(f"Создан временный пользователь {superuser.username} для назначения владельцем товаров")

        # Назначаем владельца всем товарам без владельца
        products_updated = Product.objects.filter(owner__isnull=True).update(owner=superuser)
        print(f"Назначен владелец для {products_updated} товаров")

    except Exception as e:
        print(f"Ошибка при назначении владельцев: {e}")


def reverse_populate_product_owners(apps, schema_editor):
    """
    Откат миграции - очищаем поле owner.
    """
    Product = apps.get_model('catalog', 'Product')
    Product.objects.all().update(owner=None)


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0002_add_owner_and_status'),
    ]

    operations = [
        # Заполняем владельцев существующих товаров
        migrations.RunPython(
            populate_product_owners,
            reverse_populate_product_owners
        ),

        # Делаем поле owner обязательным
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(
                help_text='Пользователь, создавший товар',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Владелец'
            ),
        ),
    ]