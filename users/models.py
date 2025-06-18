from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя с дополнительными полями.

    Наследуется от AbstractUser, что позволяет использовать всю стандартную
    функциональность Django для работы с пользователями, но с возможностью
    добавления собственных полей.
    """

    # Переопределяем email как обязательное поле
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
        help_text='Адрес электронной почты для входа в систему'
    )

    # Дополнительные поля
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Загрузите изображение для вашего профиля'
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Номер телефона',
        help_text='Контактный номер телефона'
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Страна',
        help_text='Страна проживания'
    )

    # Дата создания и обновления профиля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление профиля'
    )

    # Указываем, что для входа используется email, а не username
    USERNAME_FIELD = 'email'

    # Поля, которые будут запрашиваться при создании суперпользователя
    # username удаляем из обязательных, так как используем email
    REQUIRED_FIELDS = ['username']

    # КРИТИЧНО: Переопределяем related_name для избежания конфликтов
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Изменяем related_name
        related_query_name='custom_user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Изменяем related_name
        related_query_name='custom_user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']  # Новые пользователи первые

    def __str__(self):
        """Строковое представление пользователя."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name} ({self.email})'
        return self.email

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.email

    def get_short_name(self):
        """Возвращает короткое имя пользователя."""
        return self.first_name or self.email

    def get_avatar_url(self):
        """Возвращает URL аватара или заглушку."""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'  # Заглушка для аватара