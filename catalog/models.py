from django.db import models
from django.urls import reverse


class Category(models.Model):
    """
    Модель категории товаров.

    Категория группирует товары по типу (например, "Электроника", "Одежда").
    Это справочная модель, которая используется для классификации товаров.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
        help_text='Введите название категории'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Опишите категорию товаров'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']  # Сортировка по названию

    def __str__(self):
        """
        Строковое представление объекта категории.
        Используется в админке и при отладке.
        """
        return self.name

    def get_absolute_url(self):
        """
        Возвращает URL для детального просмотра категории.
        Пока что ведет на главную страницу, в ДЗ3 добавим страницу категории.
        """
        return reverse('catalog:home')


class Product(models.Model):
    """
    Модель товара.

    Содержит всю основную информацию о товаре: название, описание, цену,
    изображение и связь с категорией.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
        help_text='Введите название товара'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Подробное описание товара'
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Загрузите изображение товара'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория',
        help_text='Выберите категорию товара'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за покупку',
        help_text='Цена в рублях'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']  # Новые товары сначала

    def __str__(self):
        """
        Строковое представление объекта товара.
        Показываем название и цену для удобства.
        """
        return f'{self.name} - {self.price} руб.'

    def get_absolute_url(self):
        """
        Возвращает URL для детального просмотра товара.
        В ДЗ3 создадим соответствующий view и URL.
        """
        return reverse('catalog:home')

    def get_short_description(self):
        """
        Возвращает сокращенное описание товара (первые 100 символов).
        Будет использоваться в шаблонах для отображения превью.
        """
        if self.description:
            return self.description[:100] + '...' if len(self.description) > 100 else self.description
        return 'Описание отсутствует'