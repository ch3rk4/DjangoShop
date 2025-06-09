from django.db import models
from django.urls import reverse


class BlogPost(models.Model):
    """
    Модель блоговой записи.
    """

    # CharField используется для коротких текстов с ограничением длины
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Введите заголовок статьи (максимум 200 символов)'
    )

    # TextField используется для длинных текстов без ограничения длины
    content = models.TextField(
        verbose_name='Содержимое',
        help_text='Основной текст статьи'
    )

    # ImageField для загрузки изображений
    preview_image = models.ImageField(
        upload_to='blog_previews/',  # Папка, куда сохранять изображения
        blank=True,  # Поле может быть пустым в формах
        null=True,  # Поле может быть NULL в базе данных
        verbose_name='Превью изображение',
        help_text='Загрузите изображение для превью статьи'
    )

    # DateTimeField с auto_now_add автоматически устанавливает дату создания
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время создания записи (устанавливается автоматически)'
    )

    # BooleanField для хранения логических значений True/False
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
        help_text='Отметьте, чтобы статья была видна на сайте'
    )

    # PositiveIntegerField для хранения положительных чисел
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров',
        help_text='Счетчик просмотров статьи (обновляется автоматически)'
    )

    class Meta:
        """
        Метакласс определяет дополнительные параметры модели.
        """
        verbose_name = 'Блоговая запись'
        verbose_name_plural = 'Блоговые записи'
        ordering = ['-created_date']  # Сортировка по дате создания (новые первые)

        # Индексы для ускорения запросов
        indexes = [
            models.Index(fields=['-created_date']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return self.title

    def get_absolute_url(self):
        """
        Возвращает URL для просмотра конкретной записи.
        """
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def get_short_content(self, words_count=50):
        """
        Возвращает сокращенную версию контента для превью.
        """
        words = self.content.split()
        if len(words) > words_count:
            return ' '.join(words[:words_count]) + '...'
        return self.content