from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

# Получаем модель пользователя
User = get_user_model()


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
        """
        return reverse('catalog:index')


class Product(models.Model):
    """
    Модель товара.

    Содержит всю основную информацию о товаре: название, описание, цену,
    изображение и связь с категорией.
    """
    # Статусы публикации товара
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

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

    # НОВОЕ: Статус публикации
    publication_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус публикации',
        help_text='Текущий статус товара в системе'
    )

    # НОВОЕ: Владелец товара
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Владелец',
        help_text='Пользователь, создавший товар',
        null=True,  # Временно для миграции
        blank=True
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

        # НОВОЕ: Кастомные права
        permissions = [
            ('can_unpublish_product', 'Может отменять публикацию товара'),
            ('can_moderate_product', 'Может модерировать товары'),
            ('can_change_product_status', 'Может изменять статус товара'),
        ]

    def __str__(self):
        """
        Строковое представление объекта товара.
        Показываем название и цену для удобства.
        """
        return f'{self.name} - {self.price} руб.'

    def get_absolute_url(self):
        """
        Возвращает URL для детального просмотра товара.
        """
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})

    def get_short_description(self):
        """
        Возвращает сокращенное описание товара (первые 100 символов).
        Будет использоваться в шаблонах для отображения превью.
        """
        if self.description:
            return self.description[:100] + '...' if len(self.description) > 100 else self.description
        return 'Описание отсутствует'

    def is_published(self):
        """Проверяет, опубликован ли товар."""
        return self.publication_status == 'published'

    def can_be_edited_by(self, user):
        """Проверяет, может ли пользователь редактировать товар."""
        if not user.is_authenticated:
            return False
        # Владелец может редактировать
        if self.owner == user:
            return True
        # Модератор может редактировать
        if user.has_perm('catalog.can_moderate_product'):
            return True
        # Администратор может редактировать
        if user.is_superuser:
            return True
        return False

    def can_be_deleted_by(self, user):
        """Проверяет, может ли пользователь удалить товар."""
        if not user.is_authenticated:
            return False
        # Владелец может удалять
        if self.owner == user:
            return True
        # Модератор может удалять
        if user.has_perm('catalog.delete_product'):
            return True
        # Администратор может удалять
        if user.is_superuser:
            return True
        return False