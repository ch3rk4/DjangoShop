from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from catalog.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    """
    Кастомная команда для загрузки тестовых данных.

    Использование: python manage.py load_test_data
    """
    help = 'Загружает тестовые данные в базу данных'

    def add_arguments(self, parser):
        """Добавляем аргументы командной строки."""
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Создать суперпользователя если его нет',
        )

    def handle(self, *args, **options):
        """
        Основная логика команды.
        """
        self.stdout.write(
            self.style.WARNING('Начинаем загрузку тестовых данных...')
        )

        # Создаем или получаем тестового пользователя
        test_user = self.get_or_create_test_user()

        # Удаляем существующие данные
        self.stdout.write('Удаляем существующие товары...')
        Product.objects.all().delete()

        self.stdout.write('Удаляем существующие категории...')
        Category.objects.all().delete()

        # Загружаем данные из фикстур
        try:
            self.stdout.write('Загружаем категории...')
            call_command('loaddata', 'fixtures/categories.json')

            self.stdout.write('Создаем тестовые товары...')
            self.create_test_products(test_user)

            # Выводим статистику
            categories_count = Category.objects.count()
            products_count = Product.objects.count()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные успешно загружены!\n'
                    f'Категорий: {categories_count}\n'
                    f'Товаров: {products_count}\n'
                    f'Владелец товаров: {test_user.username} ({test_user.email})'
                )
            )

            # Создаем суперпользователя если нужно
            if options['create_superuser']:
                self.create_superuser_if_needed()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке данных: {e}')
            )

    def get_or_create_test_user(self):
        """Создает или получает тестового пользователя."""

        # Сначала ищем существующего суперпользователя
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            self.stdout.write(f'Используем существующего суперпользователя: {superuser.username}')
            return superuser

        # Ищем пользователя с именем 'testuser'
        try:
            test_user = User.objects.get(username='testuser')
            self.stdout.write(f'Используем существующего тестового пользователя: {test_user.username}')
            return test_user
        except User.DoesNotExist:
            pass

        # Создаем нового тестового пользователя
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Тест',
            last_name='Пользователь'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Создан тестовый пользователь: {test_user.username}')
        )

        return test_user

    def create_test_products(self, owner):
        """Создает тестовые товары."""

        # Получаем категории
        try:
            electronics = Category.objects.get(name='Электроника')
            clothing = Category.objects.get(name='Одежда')
            books = Category.objects.get(name='Книги')
        except Category.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Категория не найдена: {e}')
            )
            return

        # Создаем товары
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Новейший смартфон Apple с инновационными технологиями и улучшенной камерой. Идеальное сочетание производительности и стиля.',
                'category': electronics,
                'price': 99999.00,
                'publication_status': 'published'
            },
            {
                'name': 'MacBook Air M2',
                'description': 'Легкий и мощный ноутбук от Apple. Процессор M2 обеспечивает невероятную производительность при минимальном энергопотреблении.',
                'category': electronics,
                'price': 89999.00,
                'publication_status': 'published'
            },
            {
                'name': 'Джинсы классические',
                'description': 'Удобные джинсы из качественного денима. Классический крой подойдет для любого случая.',
                'category': clothing,
                'price': 3500.00,
                'publication_status': 'published'
            },
            {
                'name': 'Худи утепленное',
                'description': 'Теплое и стильное худи для холодного времени года. Выполнено из мягкого хлопка с утеплителем.',
                'category': clothing,
                'price': 2800.00,
                'publication_status': 'published'
            },
            {
                'name': 'Python для начинающих',
                'description': 'Отличная книга для изучения языка программирования Python с нуля. Множество практических примеров и упражнений.',
                'category': books,
                'price': 1200.00,
                'publication_status': 'published'
            },
            {
                'name': 'Ноутбук Gaming Pro',
                'description': 'Мощный игровой ноутбук для требовательных игр и задач. На модерации.',
                'category': electronics,
                'price': 125000.00,
                'publication_status': 'pending'
            },
            {
                'name': 'Черновик товара',
                'description': 'Этот товар находится в стадии разработки.',
                'category': electronics,
                'price': 15000.00,
                'publication_status': 'draft'
            },
        ]

        created_count = 0
        for product_data in products_data:
            product = Product.objects.create(
                owner=owner,
                **product_data
            )
            created_count += 1
            self.stdout.write(f'  ✓ Создан товар: {product.name} ({product.get_publication_status_display()})')

        self.stdout.write(
            self.style.SUCCESS(f'Создано товаров: {created_count}')
        )

    def create_superuser_if_needed(self):
        """Создает суперпользователя если его еще нет."""

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Суперпользователь уже существует')
            return

        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Админ',
            last_name='Администратор'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Создан суперпользователь: {admin_user.username}\n'
                f'Пароль: admin123'
            )
        )