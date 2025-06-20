from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    """
    Команда для создания групп пользователей с настроенными правами.

    Использование: python manage.py create_groups
    """
    help = 'Создает группы пользователей с правами: Модератор продуктов, Контент-менеджер'

    def handle(self, *args, **options):
        """
        Основная логика команды.
        """
        self.stdout.write(
            self.style.WARNING('Начинаем создание групп и настройку прав...')
        )

        # Создаем группу "Модератор продуктов"
        self.create_product_moderator_group()

        # Создаем группу "Контент-менеджер"
        self.create_content_manager_group()

        self.stdout.write(
            self.style.SUCCESS('Все группы успешно созданы!')
        )

    def create_product_moderator_group(self):
        """Создает группу модераторов продуктов."""
        group_name = 'Модератор продуктов'

        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(f'Создана группа: {group_name}')
        else:
            self.stdout.write(f'Группа уже существует: {group_name}')
            # Очищаем существующие права для переназначения
            group.permissions.clear()

        # Получаем content type для модели Product
        product_ct = ContentType.objects.get_for_model(Product)

        # Список прав для модератора продуктов
        permissions_codenames = [
            'can_unpublish_product',  # Кастомное право на отмену публикации
            'can_moderate_product',  # Кастомное право на модерацию
            'can_change_product_status',  # Кастомное право на изменение статуса
            'change_product',  # Стандартное право на изменение
            'delete_product',  # Стандартное право на удаление
            'view_product',  # Стандартное право на просмотр
        ]

        # Добавляем права в группу
        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=product_ct
                )
                group.permissions.add(permission)
                self.stdout.write(f'  ✓ Добавлено право: {permission.name}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Право не найдено: {codename}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Группа "{group_name}" настроена')
        )

    def create_content_manager_group(self):
        """Создает группу контент-менеджеров для блога."""
        group_name = 'Контент-менеджер'

        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(f'Создана группа: {group_name}')
        else:
            self.stdout.write(f'Группа уже существует: {group_name}')
            # Очищаем существующие права для переназначения
            group.permissions.clear()

        # Получаем content type для модели BlogPost
        blogpost_ct = ContentType.objects.get_for_model(BlogPost)

        # Список прав для контент-менеджера
        permissions_codenames = [
            'add_blogpost',  # Создание статей
            'change_blogpost',  # Изменение статей
            'delete_blogpost',  # Удаление статей
            'view_blogpost',  # Просмотр статей
        ]

        # Добавляем права в группу
        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=blogpost_ct
                )
                group.permissions.add(permission)
                self.stdout.write(f'  ✓ Добавлено право: {permission.name}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Право не найдено: {codename}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Группа "{group_name}" настроена')
        )

    def show_statistics(self):
        """Показывает статистику по группам."""
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('СТАТИСТИКА ГРУПП:')
        self.stdout.write('=' * 50)

        for group in Group.objects.all():
            self.stdout.write(f'\nГруппа: {group.name}')
            self.stdout.write(f'Количество прав: {group.permissions.count()}')
            self.stdout.write(f'Количество пользователей: {group.user_set.count()}')

            if group.permissions.exists():
                self.stdout.write('Права:')
                for perm in group.permissions.all():
                    self.stdout.write(f'  - {perm.name} ({perm.codename})')