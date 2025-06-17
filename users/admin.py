from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомная админка для пользователей.

    Расширяет стандартную админку Django для работы с нашей кастомной
    моделью пользователя, добавляя новые поля.
    """

    # Поля для отображения в списке пользователей
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'country', 'is_staff', 'is_active', 'created_at'
    )

    # Поля для поиска
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')

    # Фильтры в боковой панели
    list_filter = ('is_staff', 'is_active', 'country', 'created_at')

    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    # Переопределяем fieldsets для формы редактирования пользователя
    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'username', 'password')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'avatar', 'phone_number', 'country')
        }),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)  # Секция будет свернута по умолчанию
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Поля для формы добавления нового пользователя
    add_fieldsets = (
        ('Обязательная информация', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Дополнительная информация', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number', 'country'),
        }),
    )

    # Сортировка по умолчанию
    ordering = ('-created_at',)

    # Количество пользователей на странице
    list_per_page = 25