from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели BlogPost в админке.

    Это как настройка приборной панели автомобиля -
    мы определяем, какие данные показывать и как ими управлять.
    """

    # Поля, которые отображаются в списке записей
    list_display = [
        'title',  # Заголовок статьи
        'created_date',  # Дата создания
        'is_published',  # Статус публикации
        'views_count',  # Количество просмотров
        'get_short_content'  # Краткое содержимое
    ]

    # Поля, по которым можно фильтровать записи
    list_filter = [
        'is_published',  # Фильтр по статусу публикации
        'created_date',  # Фильтр по дате создания
    ]

    # Поля, по которым работает поиск
    search_fields = [
        'title',  # Поиск по заголовку
        'content',  # Поиск по содержимому
    ]

    # Поля, которые можно редактировать прямо в списке (без открытия отдельной страницы)
    list_editable = [
        'is_published',  # Можно быстро публиковать/снимать с публикации
    ]

    # Поля только для чтения (их нельзя редактировать)
    readonly_fields = [
        'created_date',  # Дата создания не должна изменяться
        'views_count',  # Количество просмотров изменяется автоматически
    ]

    # Организация полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'preview_image')
        }),
        ('Настройки публикации', {
            'fields': ('is_published',)
        }),
        ('Статистика', {
            'fields': ('created_date', 'views_count'),
            'classes': ('collapse',),  # Секция будет свернута по умолчанию
        }),
    )

    # Сколько записей показывать на одной странице
    list_per_page = 20

    # Автоматическое сохранение черновиков
    save_on_top = True

    def get_short_content(self, obj):
        """Показывает краткое содержимое в списке записей."""
        return obj.get_short_content(20)  # Первые 20 слов

    get_short_content.short_description = 'Краткое содержимое'