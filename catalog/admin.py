from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Category в админке.
    """
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Секция будет свернута по умолчанию
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Product в админке.
    """
    list_display = ('id', 'name', 'price', 'category', 'owner', 'status_badge', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('category', 'publication_status', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username', 'owner__email')
    list_select_related = ('category', 'owner')  # Оптимизация запросов
    readonly_fields = ('created_at', 'updated_at')

    # Поля, которые можно редактировать прямо в списке
    list_editable = ('publication_status',)

    # Фильтры для быстрого поиска
    list_filter = (
        'publication_status',
        'category',
        ('owner', admin.RelatedOnlyFieldListFilter),
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'price', 'image')
        }),
        ('Права и статус', {
            'fields': ('owner', 'publication_status')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Автокомплит для связанных полей
    autocomplete_fields = ['owner', 'category']

    # Количество объектов на странице
    list_per_page = 25

    def status_badge(self, obj):
        """Отображает статус как цветной бейдж."""
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'published': '#28a745',
            'unpublished': '#dc3545',
        }

        color = colors.get(obj.publication_status, '#6c757d')
        status_text = obj.get_publication_status_display()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            status_text
        )

    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'publication_status'

    def get_queryset(self, request):
        """Оптимизируем запросы."""
        return super().get_queryset(request).select_related(
            'category', 'owner'
        ).prefetch_related('owner__groups')

    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем владельца при создании."""
        if not change:  # Если создаем новый объект
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Проверяем права на изменение."""
        if obj is None:
            return True

        # Суперпользователь может все
        if request.user.is_superuser:
            return True

        # Владелец может редактировать
        if obj.owner == request.user:
            return True

        # Модераторы могут редактировать
        if request.user.has_perm('catalog.can_moderate_products'):
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        """Проверяем права на удаление."""
        if obj is None:
            return True

        # Суперпользователь может все
        if request.user.is_superuser:
            return True

        # Владелец может удалить
        if obj.owner == request.user:
            return True

        # Модераторы продуктов могут удалить
        if request.user.groups.filter(name='Модератор продуктов').exists():
            return True

        return False

    actions = ['publish_products', 'unpublish_products', 'set_pending']

    def publish_products(self, request, queryset):
        """Действие для публикации товаров."""
        updated = queryset.update(publication_status='published')
        self.message_user(
            request,
            f'Опубликовано товаров: {updated}'
        )

    publish_products.short_description = 'Опубликовать выбранные товары'

    def unpublish_products(self, request, queryset):
        """Действие для снятия товаров с публикации."""
        # Проверяем права
        if not request.user.has_perm('catalog.can_unpublish_product'):
            self.message_user(
                request,
                'У вас нет прав для снятия товаров с публикации',
                level='ERROR'
            )
            return

        updated = queryset.update(publication_status='unpublished')
        self.message_user(
            request,
            f'Снято с публикации товаров: {updated}'
        )

    unpublish_products.short_description = 'Снять с публикации выбранные товары'

    def set_pending(self, request, queryset):
        """Действие для отправки товаров на модерацию."""
        updated = queryset.update(publication_status='pending')
        self.message_user(
            request,
            f'Отправлено на модерацию товаров: {updated}'
        )

    set_pending.short_description = 'Отправить на модерацию'