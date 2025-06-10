from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    """
    Кастомная команда для загрузки тестовых данных.

    Использование: python manage.py load_test_data
    """
    help = 'Загружает тестовые данные в базу данных'

    def handle(self, *args, **options):
        """
        Основная логика команды.
        """
        self.stdout.write(
            self.style.WARNING('Начинаем загрузку тестовых данных...')
        )

        # Удаляем существующие данные
        self.stdout.write('Удаляем существующие товары...')
        Product.objects.all().delete()

        self.stdout.write('Удаляем существующие категории...')
        Category.objects.all().delete()

        # Загружаем данные из фикстур
        try:
            self.stdout.write('Загружаем категории...')
            call_command('loaddata', 'fixtures/categories.json')

            self.stdout.write('Загружаем товары...')
            call_command('loaddata', 'fixtures/products.json')

            # Выводим статистику
            categories_count = Category.objects.count()
            products_count = Product.objects.count()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные успешно загружены!\n'
                    f'Категорий: {categories_count}\n'
                    f'Товаров: {products_count}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке данных: {e}')
            )