from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
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
    list_filter = ('is_staff', 'is_active', 'country', 'created_at', 'is_superuser')

    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    # Сортировка по умолчанию
    ordering = ('-created_at',)

    # Переопределяем fieldsets для формы редактирования пользователя
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'phone_number', 'country')
        }),
        ('Разрешения', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Поля для формы добавления нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Дополнительная информация', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number', 'country'),
        }),
        ('Разрешения', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Количество пользователей на странице
    list_per_page = 25

    def get_form(self, request, obj=None, **kwargs):
        """
        Переопределяем форму для лучшей работы с email как USERNAME_FIELD.
        """
        form = super().get_form(request, obj, **kwargs)

        # Делаем email обязательным
        if 'email' in form.base_fields:
            form.base_fields['email'].required = True

        return form

    def save_model(self, request, obj, form, change):
        """
        Дополнительная логика при сохранении пользователя.
        """
        # Убеждаемся, что email в нижнем регистре
        if hasattr(obj, 'email') and obj.email:
            obj.email = obj.email.lower()

        super().save_model(request, obj, form, change)