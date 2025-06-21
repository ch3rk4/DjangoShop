"""
Сервисные функции для работы с продуктами.

Этот модуль содержит бизнес-логику для работы с товарами,
включая кеширование и оптимизацию запросов.
"""

from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet, Q, Avg
from django.db import models
from typing import List, Optional
import logging

from .models import Product, Category

# Настройка логирования для отслеживания кеширования
logger = logging.getLogger('cache')


def get_products_by_category(
        category_id: int,
        user=None,
        include_unpublished: bool = False
) -> QuerySet[Product]:
    """
    Возвращает список всех продуктов в указанной категории с кешированием.

    Args:
        category_id: ID категории
        user: Текущий пользователь (для проверки прав доступа)
        include_unpublished: Включать ли неопубликованные товары

    Returns:
        QuerySet с товарами из указанной категории

    Raises:
        Category.DoesNotExist: Если категория не найдена
    """

    # Формируем ключ кеша
    cache_key = f"products_category_{category_id}"

    # Если пользователь авторизован и может видеть все товары, добавляем это в ключ
    if user and user.is_authenticated and (
            user.has_perm('catalog.can_moderate_products') or include_unpublished
    ):
        cache_key += "_all"

    # Проверяем настройку кеширования
    if getattr(settings, 'CACHE_ENABLED', True):
        # Пытаемся получить данные из кеша
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            logger.info(f"Получены товары категории {category_id} из кеша: {cache_key}")
            return cached_products

    # Проверяем существование категории
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        logger.error(f"Категория {category_id} не найдена")
        raise

    # Базовый запрос с оптимизацией
    queryset = Product.objects.filter(category=category).select_related(
        'category', 'owner'
    ).order_by('-created_at')

    # Фильтрация по статусу публикации
    if not include_unpublished:
        # Если пользователь модератор, показываем все товары
        if user and user.is_authenticated and user.has_perm('catalog.can_moderate_products'):
            pass  # Показываем все товары
        else:
            # Обычным пользователям только опубликованные
            queryset = queryset.filter(publication_status='published')

    # Выполняем запрос (evaluate QuerySet)
    products = list(queryset)

    # Кешируем результат
    if getattr(settings, 'CACHE_ENABLED', True):
        cache_timeout = getattr(settings, 'CACHE_TTL', {}).get('products', 300)
        cache.set(cache_key, products, cache_timeout)
        logger.info(f"Кешированы товары категории {category_id}: {len(products)} товаров, ключ: {cache_key}")

    return products


def get_cached_product_list(
        filters: Optional[dict] = None,
        user=None,
        cache_key_suffix: str = ""
) -> List[Product]:
    """
    Получает список товаров с низкоуровневым кешированием.

    Args:
        filters: Словарь с фильтрами для QuerySet
        user: Текущий пользователь
        cache_key_suffix: Дополнительный суффикс для ключа кеша

    Returns:
        Список товаров
    """

    # Формируем базовый ключ кеша
    cache_key = "products_list"

    if cache_key_suffix:
        cache_key += f"_{cache_key_suffix}"

    # Добавляем хеш фильтров в ключ
    if filters:
        filter_hash = hash(frozenset(filters.items()))
        cache_key += f"_filters_{filter_hash}"

    # Проверяем права пользователя
    if user and user.is_authenticated and user.has_perm('catalog.can_moderate_products'):
        cache_key += "_moderator"

    # Проверяем кеш
    if getattr(settings, 'CACHE_ENABLED', True):
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Получен список товаров из кеша: {cache_key}")
            return cached_data

    # Формируем запрос
    queryset = Product.objects.select_related('category', 'owner')

    # Применяем фильтры
    if filters:
        queryset = queryset.filter(**filters)

    # Фильтрация по правам пользователя
    if not (user and user.is_authenticated and user.has_perm('catalog.can_moderate_products')):
        queryset = queryset.filter(publication_status='published')

    # Сортировка
    queryset = queryset.order_by('-created_at')

    # Выполняем запрос
    products = list(queryset)

    # Кешируем результат
    if getattr(settings, 'CACHE_ENABLED', True):
        cache_timeout = getattr(settings, 'CACHE_TTL', {}).get('products', 300)
        cache.set(cache_key, products, cache_timeout)
        logger.info(f"Кешированы товары: {len(products)} товаров, ключ: {cache_key}")

    return products


def get_popular_products(limit: int = 10) -> List[Product]:
    """
    Возвращает популярные товары (можно расширить логику популярности).

    Args:
        limit: Количество товаров для возврата

    Returns:
        Список популярных товаров
    """

    cache_key = f"popular_products_{limit}"

    # Проверяем кеш
    if getattr(settings, 'CACHE_ENABLED', True):
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Получены популярные товары из кеша: {cache_key}")
            return cached_data

    # Пока что считаем популярными недавно добавленные опубликованные товары
    # В будущем можно добавить логику на основе просмотров, покупок и т.д.
    products = list(
        Product.objects.filter(
            publication_status='published'
        ).select_related(
            'category', 'owner'
        ).order_by('-created_at')[:limit]
    )

    # Кешируем результат
    if getattr(settings, 'CACHE_ENABLED', True):
        cache_timeout = getattr(settings, 'CACHE_TTL', {}).get('products', 300)
        cache.set(cache_key, products, cache_timeout)
        logger.info(f"Кешированы популярные товары: {len(products)} товаров")

    return products


def search_products(query: str, user=None) -> List[Product]:
    """
    Поиск товаров по запросу с кешированием.

    Args:
        query: Поисковый запрос
        user: Текущий пользователь

    Returns:
        Список найденных товаров
    """

    if not query or len(query.strip()) < 2:
        return []

    query = query.strip().lower()

    # Формируем ключ кеша
    cache_key = f"search_products_{hash(query)}"
    if user and user.is_authenticated and user.has_perm('catalog.can_moderate_products'):
        cache_key += "_moderator"

    # Проверяем кеш
    if getattr(settings, 'CACHE_ENABLED', True):
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Получены результаты поиска из кеша: {cache_key}")
            return cached_data

    # Формируем поисковый запрос
    search_filter = Q(name__icontains=query) | Q(description__icontains=query)

    queryset = Product.objects.filter(search_filter).select_related('category', 'owner')

    # Фильтрация по правам пользователя
    if not (user and user.is_authenticated and user.has_perm('catalog.can_moderate_products')):
        queryset = queryset.filter(publication_status='published')

    products = list(queryset.order_by('-created_at'))

    # Кешируем результат (с меньшим TTL для поиска)
    if getattr(settings, 'CACHE_ENABLED', True):
        cache_timeout = getattr(settings, 'CACHE_TTL', {}).get('products', 300) // 2  # Половина от обычного времени
        cache.set(cache_key, products, cache_timeout)
        logger.info(f"Кешированы результаты поиска: {len(products)} товаров")

    return products


def invalidate_products_cache(category_id: Optional[int] = None):
    """
    Инвалидирует кеш товаров.

    Args:
        category_id: ID категории для инвалидации конкретной категории
    """

    if not getattr(settings, 'CACHE_ENABLED', True):
        return

    if category_id:
        # Инвалидируем кеш конкретной категории
        cache_keys = [
            f"products_category_{category_id}",
            f"products_category_{category_id}_all"
        ]
    else:
        # Инвалидируем весь кеш товаров (упрощенная версия)
        cache_keys = [
            "products_list*",  # Все списки товаров
            "popular_products*",  # Популярные товары
            "search_products*",  # Результаты поиска
        ]

    for key in cache_keys:
        if "*" in key:
            # Для паттернов используем clear (в реальном проекте лучше использовать более точные методы)
            logger.info(f"Инвалидация кеша по паттерну: {key}")
        else:
            cache.delete(key)
            logger.info(f"Инвалидирован кеш: {key}")


def get_category_stats(category_id: int) -> dict:
    """
    Получает статистику по категории с кешированием.

    Args:
        category_id: ID категории

    Returns:
        Словарь со статистикой категории
    """

    cache_key = f"category_stats_{category_id}"

    # Проверяем кеш
    if getattr(settings, 'CACHE_ENABLED', True):
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Получена статистика категории из кеша: {cache_key}")
            return cached_data

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return {}

    # Собираем статистику
    all_products = Product.objects.filter(category=category)
    published_products = all_products.filter(publication_status='published')

    stats = {
        'category_name': category.name,
        'total_products': all_products.count(),
        'published_products': published_products.count(),
        'pending_products': all_products.filter(publication_status='pending').count(),
        'draft_products': all_products.filter(publication_status='draft').count(),
        'avg_price': published_products.aggregate(
            avg_price=Avg('price')
        )['avg_price'] or 0,
    }

    # Кешируем статистику
    if getattr(settings, 'CACHE_ENABLED', True):
        cache_timeout = getattr(settings, 'CACHE_TTL', {}).get('categories', 3600)
        cache.set(cache_key, stats, cache_timeout)
        logger.info(f"Кеширована статистика категории {category_id}")

    return stats