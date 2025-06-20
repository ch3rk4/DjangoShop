from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    """
    Команда для создания групп и настройки прав доступа.

    Использование: python manage.py setup_groups
    """
    help = 'Создает группы пользователей и настраивает права доступа'

    def handle(self, *args, **options):
        """Основная логика команды."""

        self.stdout.write(
            self.style.WARNING('Начинаем настройку групп и прав доступа...')
        )

        # Получаем типы контента для наших моделей
        product_content_type = ContentType.objects.get_for_model(Product)
        blog_content_type = ContentType.objects.get_for_model(BlogPost)

        # Создаем группу "Модератор продуктов"
        self.create_product_moderator_group(product_content_type)

        # Создаем группу "Контент-менеджер"
        self.create_content_manager_group(blog_content_type)

        self.stdout.write(
            self.style.SUCCESS('✅ Группы и права доступа успешно настроены!')
        )

    def create_product_moderator_group(self, product_content_type):
        """Создает группу модератора продуктов."""

        self.stdout.write('Создаем группу "Модератор продуктов"...')

        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Группа создана'))
        else:
            self.stdout.write('  ℹ️ Группа уже существует, обновляем права')

        # Список необходимых прав
        required_permissions = [
            # Кастомные права
            'can_unpublish_product',
            'can_moderate_products',
            # Стандартные права Django
            'delete_product',  # Право на удаление продуктов
            'change_product',  # Право на изменение продуктов
            'view_product',  # Право на просмотр продуктов
        ]

        # Добавляем права к группе
        added_permissions = []
        for perm_codename in required_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=product_content_type
                )
                group.permissions.add(permission)
                added_permissions.append(perm_codename)

            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Право {perm_codename} не найдено')
                )

        self.stdout.write(
            self.style.SUCCESS(f'  ✅ Добавлено прав: {len(added_permissions)}')
        )

        for perm in added_permissions:
            self.stdout.write(f'    - {perm}')

    def create_content_manager_group(self, blog_content_type):
        """Создает группу контент-менеджера."""

        self.stdout.write('Создаем группу "Контент-менеджер"...')

        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(name='Контент-менеджер')

        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Группа создана'))
        else:
            self.stdout.write('  ℹ️ Группа уже существует, обновляем права')

        # Список необходимых прав для блога
        required_permissions = [
            'add_blogpost',  # Создание статей
            'change_blogpost',  # Редактирование статей
            'delete_blogpost',  # Удаление статей
            'view_blogpost',  # Просмотр статей
        ]

        # Добавляем права к группе
        added_permissions = []
        for perm_codename in required_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=blog_content_type
                )
                group.permissions.add(permission)
                added_permissions.append(perm_codename)

            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Право {perm_codename} не найдено')
                )

        self.stdout.write(
            self.style.SUCCESS(f'  ✅ Добавлено прав: {len(added_permissions)}')
        )

        for perm in added_permissions:
            self.stdout.write(f'    - {perm}')

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие группы и создать заново',
        )