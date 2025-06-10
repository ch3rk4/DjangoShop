#!/usr/bin/env python
"""
Скрипт для тестирования CRUD операций с продуктами.
Запуск: python test_crud.py
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product, Category
from catalog.forms import ProductForm
from django.core.files.uploadedfile import SimpleUploadedFile


def test_forbidden_words():
    """Тестирует валидацию запрещенных слов."""
    print("🧪 Тестирование валидации запрещенных слов...")

    # Создаем тестовую категорию
    category, created = Category.objects.get_or_create(
        name="Тестовая категория",
        defaults={'description': 'Для тестирования'}
    )

    # Тест 1: Запрещенное слово в названии
    form_data = {
        'name': 'Лучшее казино в городе',
        'description': 'Описание товара',
        'category': category.id,
        'price': '1000.00'
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid(), "Форма должна быть невалидной при запрещенном слове в названии"
    assert 'name' in form.errors, "Должна быть ошибка в поле name"
    print("✅ Тест запрещенного слова в названии прошел")

    # Тест 2: Запрещенное слово в описании
    form_data = {
        'name': 'Нормальный товар',
        'description': 'Это не обман, товар действительно хороший',
        'category': category.id,
        'price': '1000.00'
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid(), "Форма должна быть невалидной при запрещенном слове в описании"
    assert 'description' in form.errors, "Должна быть ошибка в поле description"
    print("✅ Тест запрещенного слова в описании прошел")

    # Тест 3: Валидные данные
    form_data = {
        'name': 'Хороший товар',
        'description': 'Качественный товар по доступной цене',
        'category': category.id,
        'price': '1000.00'
    }
    form = ProductForm(data=form_data)
    assert form.is_valid(), f"Форма должна быть валидной для корректных данных. Ошибки: {form.errors}"
    print("✅ Тест валидных данных прошел")


def test_price_validation():
    """Тестирует валидацию цены."""
    print("\n🧪 Тестирование валидации цены...")

    category, created = Category.objects.get_or_create(
        name="Тестовая категория",
        defaults={'description': 'Для тестирования'}
    )

    # Тест 1: Отрицательная цена
    form_data = {
        'name': 'Товар с отрицательной ценой',
        'description': 'Описание',
        'category': category.id,
        'price': '-100.00'
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid(), "Форма должна быть невалидной при отрицательной цене"
    assert 'price' in form.errors, "Должна быть ошибка в поле price"
    print("✅ Тест отрицательной цены прошел")

    # Тест 2: Нулевая цена
    form_data = {
        'name': 'Товар с нулевой ценой',
        'description': 'Описание',
        'category': category.id,
        'price': '0.00'
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid(), "Форма должна быть невалидной при нулевой цене"
    assert 'price' in form.errors, "Должна быть ошибка в поле price"
    print("✅ Тест нулевой цены прошел")

    # Тест 3: Слишком большая цена
    form_data = {
        'name': 'Дорогой товар',
        'description': 'Описание',
        'category': category.id,
        'price': '1000000.00'
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid(), "Форма должна быть невалидной при слишком большой цене"
    assert 'price' in form.errors, "Должна быть ошибка в поле price"
    print("✅ Тест слишком большой цены прошел")


def test_image_validation():
    """Тестирует валидацию изображений."""
    print("\n🧪 Тестирование валидации изображений...")

    category, created = Category.objects.get_or_create(
        name="Тестовая категория",
        defaults={'description': 'Для тестирования'}
    )

    # Тест 1: Неправильный формат файла
    form_data = {
        'name': 'Товар с неправильным изображением',
        'description': 'Описание',
        'category': category.id,
        'price': '1000.00'
    }

    # Создаем фейковый файл неправильного формата
    fake_file = SimpleUploadedFile(
        "test.txt",
        b"file_content",
        content_type="text/plain"
    )

    form = ProductForm(data=form_data, files={'image': fake_file})
    assert not form.is_valid(), "Форма должна быть невалидной при неправильном формате изображения"
    assert 'image' in form.errors, "Должна быть ошибка в поле image"
    print("✅ Тест неправильного формата изображения прошел")


def test_crud_operations():
    """Тестирует CRUD операции."""
    print("\n🧪 Тестирование CRUD операций...")

    # Создаем категорию
    category, created = Category.objects.get_or_create(
        name="CRUD Тест",
        defaults={'description': 'Для тестирования CRUD'}
    )

    # CREATE - Создание
    product = Product.objects.create(
        name="CRUD Тест Товар",
        description="Тестовое описание для CRUD операций",
        category=category,
        price=999.99
    )
    assert product.id is not None, "Товар должен быть создан с ID"
    print("✅ CREATE - Товар создан")

    # READ - Чтение
    found_product = Product.objects.get(id=product.id)
    assert found_product.name == "CRUD Тест Товар", "Товар должен быть найден по ID"
    print("✅ READ - Товар найден")

    # UPDATE - Обновление
    found_product.name = "Обновленный CRUD Товар"
    found_product.price = 1999.99
    found_product.save()

    updated_product = Product.objects.get(id=product.id)
    assert updated_product.name == "Обновленный CRUD Товар", "Название должно быть обновлено"
    assert updated_product.price == 1999.99, "Цена должна быть обновлена"
    print("✅ UPDATE - Товар обновлен")

    # DELETE - Удаление
    product_id = updated_product.id
    updated_product.delete()

    try:
        Product.objects.get(id=product_id)
        assert False, "Товар должен быть удален"
    except Product.DoesNotExist:
        print("✅ DELETE - Товар удален")


def test_form_styling():
    """Тестирует стилизацию формы."""
    print("\n🧪 Тестирование стилизации формы...")

    form = ProductForm()

    # Проверяем, что поля имеют правильные CSS классы
    assert 'form-control' in form.fields['name'].widget.attrs.get('class',
                                                                  ''), "Поле name должно иметь класс form-control"
    assert 'form-control' in form.fields['description'].widget.attrs.get('class',
                                                                         ''), "Поле description должно иметь класс form-control"
    assert 'form-select' in form.fields['category'].widget.attrs.get('class',
                                                                     ''), "Поле category должно иметь класс form-select"
    assert 'form-control' in form.fields['price'].widget.attrs.get('class',
                                                                   ''), "Поле price должно иметь класс form-control"
    assert 'form-control' in form.fields['image'].widget.attrs.get('class',
                                                                   ''), "Поле image должно иметь класс form-control"

    print("✅ Стилизация формы корректна")


def main():
    """Запускает все тесты."""
    print("🚀 Начинаем тестирование CRUD системы для продуктов...\n")

    try:
        test_forbidden_words()
        test_price_validation()
        test_image_validation()
        test_crud_operations()
        test_form_styling()

        print("\n🎉 Все тесты прошли успешно!")
        print("✅ CRUD система работает корректно")
        print("✅ Валидация запрещенных слов работает")
        print("✅ Валидация цены работает")
        print("✅ Валидация изображений работает")
        print("✅ Стилизация формы применена")

    except Exception as e:
        print(f"\n❌ Тест провален: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())