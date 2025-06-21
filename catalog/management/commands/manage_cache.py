from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from catalog.services import invalidate_products_cache
import redis


class Command(BaseCommand):
    """
    Команда для управления кешем Redis.

    Использование:
        python manage.py manage_cache --status
        python manage.py manage_cache --clear
        python manage.py manage_cache --test
        python manage.py manage_cache --stats
    """

    help = 'Управление Redis кешем'

    def add_arguments(self, parser):
        """Добавляем аргументы командной строки."""
        parser.add_argument(
            '--status',
            action='store_true',
            help='Показать статус кеша',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить весь кеш',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Протестировать работу кеша',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Показать статистику кеша',
        )
        parser.add_argument(
            '--invalidate-products',
            action='store_true',
            help='Инвалидировать кеш товаров',
        )

    def handle(self, *args, **options):
        """Основная логика команды."""

        self.stdout.write(
            self.style.WARNING('🔧 Управление Redis кешем для Django Shop')
        )

        if not getattr(settings, 'CACHE_ENABLED', True):
            self.stdout.write(
                self.style.ERROR('❌ Кеширование отключено в настройках')
            )
            return

        if options['status']:
            self.show_cache_status()
        elif options['clear']:
            self.clear_cache()
        elif options['test']:
            self.test_cache()
        elif options['stats']:
            self.show_cache_stats()
        elif options['invalidate_products']:
            self.invalidate_products_cache()
        else:
            self.show_help()

    def show_cache_status(self):
        """Показывает статус кеша."""
        self.stdout.write('\n📊 Статус кеширования:')

        try:
            # Проверяем подключение к Redis
            cache.set('test_connection', 'ok', 30)
            result = cache.get('test_connection')

            if result == 'ok':
                self.stdout.write(
                    self.style.SUCCESS('✅ Redis подключен и работает')
                )

                # Получаем информацию о Redis
                try:
                    from django_redis import get_redis_connection
                    redis_conn = get_redis_connection("default")
                    info = redis_conn.info()

                    self.stdout.write(f"📌 Версия Redis: {info.get('redis_version', 'неизвестно')}")
                    self.stdout.write(f"📌 Используется памяти: {info.get('used_memory_human', 'неизвестно')}")
                    self.stdout.write(f"📌 Подключенных клиентов: {info.get('connected_clients', 'неизвестно')}")

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Не удалось получить детальную информацию: {e}')
                    )

            else:
                self.stdout.write(
                    self.style.ERROR('❌ Redis недоступен')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка подключения к Redis: {e}')
            )

    def clear_cache(self):
        """Очищает весь кеш."""
        self.stdout.write('\n🧹 Очистка кеша...')

        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('✅ Кеш успешно очищен')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка очистки кеша: {e}')
            )

    def test_cache(self):
        """Тестирует работу кеша."""
        self.stdout.write('\n🧪 Тестирование кеша...')

        import time
        import random

        # Тест 1: Простая запись и чтение
        test_key = f'test_{random.randint(1000, 9999)}'
        test_value = f'test_value_{random.randint(1000, 9999)}'

        try:
            # Запись
            start_time = time.time()
            cache.set(test_key, test_value, 60)
            write_time = (time.time() - start_time) * 1000

            # Чтение
            start_time = time.time()
            cached_value = cache.get(test_key)
            read_time = (time.time() - start_time) * 1000

            if cached_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Тест записи/чтения прошел успешно')
                )
                self.stdout.write(f'⏱️ Время записи: {write_time:.2f}ms')
                self.stdout.write(f'⏱️ Время чтения: {read_time:.2f}ms')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Тест записи/чтения провален')
                )

            # Очищаем тестовый ключ
            cache.delete(test_key)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка тестирования: {e}')
            )

        # Тест 2: Проверка TTL
        self.stdout.write('\n🕐 Тестирование TTL...')

        try:
            ttl_key = f'ttl_test_{random.randint(1000, 9999)}'
            cache.set(ttl_key, 'ttl_value', 2)  # 2 секунды

            # Проверяем, что значение есть
            if cache.get(ttl_key):
                self.stdout.write('✅ Значение записано с TTL')

                # Ждем истечения TTL
                self.stdout.write('⏳ Ожидание истечения TTL (3 секунды)...')
                time.sleep(3)

                # Проверяем, что значение исчезло
                if cache.get(ttl_key) is None:
                    self.stdout.write(
                        self.style.SUCCESS('✅ TTL работает корректно')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ TTL не работает')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Не удалось записать значение с TTL')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка тестирования TTL: {e}')
            )

    def show_cache_stats(self):
        """Показывает статистику кеша."""
        self.stdout.write('\n📈 Статистика кеша:')

        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            # Получаем все ключи с нашим префиксом
            keys = redis_conn.keys('djangoshop:*')

            self.stdout.write(f'📊 Всего ключей: {len(keys)}')

            if keys:
                # Группируем ключи по типам
                key_types = {}
                for key in keys[:50]:  # Ограничиваем количество для анализа
                    key_str = key.decode('utf-8')
                    key_parts = key_str.split(':')
                    if len(key_parts) >= 2:
                        key_type = key_parts[1].split('_')[0]
                        key_types[key_type] = key_types.get(key_type, 0) + 1

                self.stdout.write('\n📋 Типы ключей:')
                for key_type, count in sorted(key_types.items()):
                    self.stdout.write(f'  • {key_type}: {count}')

                # Показываем примеры ключей
                self.stdout.write('\n🔑 Примеры ключей:')
                for key in keys[:10]:
                    key_str = key.decode('utf-8')
                    ttl = redis_conn.ttl(key)
                    ttl_info = f" (TTL: {ttl}s)" if ttl > 0 else " (постоянный)" if ttl == -1 else " (истекший)"
                    self.stdout.write(f'  • {key_str}{ttl_info}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка получения статистики: {e}')
            )

    def invalidate_products_cache(self):
        """Инвалидирует кеш товаров."""
        self.stdout.write('\n🗑️ Инвалидация кеша товаров...')

        try:
            invalidate_products_cache()
            self.stdout.write(
                self.style.SUCCESS('✅ Кеш товаров инвалидирован')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка инвалидации кеша: {e}')
            )

    def show_help(self):
        """Показывает справку по команде."""
        self.stdout.write('\n📖 Доступные опции:')
        self.stdout.write('  --status              Показать статус кеша')
        self.stdout.write('  --clear               Очистить весь кеш')
        self.stdout.write('  --test                Протестировать работу кеша')
        self.stdout.write('  --stats               Показать статистику кеша')
        self.stdout.write('  --invalidate-products Инвалидировать кеш товаров')
        self.stdout.write('\nПример: python manage.py manage_cache --status')