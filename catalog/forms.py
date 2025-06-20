from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category
import os


class ProductForm(forms.ModelForm):
    """
    Форма для создания и редактирования товаров.

    Эта форма включает в себя:
    - Валидацию на запрещенные слова в названии и описании
    - Валидацию цены (не может быть отрицательной)
    - Валидацию загружаемых изображений (формат и размер)
    - Красивую стилизацию полей через Bootstrap
    - Возможность изменения статуса публикации (для модераторов)
    """

    # Константы с запрещенными словами для переиспользования
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    # Максимальный размер файла изображения (5 МБ)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ в байтах

    # Разрешенные форматы изображений
    ALLOWED_IMAGE_FORMATS = ['jpeg', 'jpg', 'png']

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'image', 'publication_status']

        # Переопределяем подписи для полей
        labels = {
            'name': 'Название товара',
            'description': 'Описание товара',
            'category': 'Категория',
            'price': 'Цена (руб.)',
            'image': 'Изображение товара',
            'publication_status': 'Статус публикации'
        }

        # Добавляем текст помощи для полей
        help_texts = {
            'name': 'Введите краткое и понятное название товара (без запрещенных слов)',
            'description': 'Подробное описание товара, его характеристики и преимущества',
            'category': 'Выберите подходящую категорию для товара',
            'price': 'Цена товара в рублях (должна быть положительным числом)',
            'image': 'Загрузите изображение товара (форматы: JPG, PNG, размер до 5 МБ)',
            'publication_status': 'Статус публикации товара'
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы с применением стилизации Bootstrap.
        """
        # Получаем пользователя из kwargs
        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        # Применяем стили Bootstrap ко всем полям с явными ID
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите название товара',
            'maxlength': '200',
            'id': 'product-name-field'
        })

        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Опишите товар подробно...',
            'id': 'product-description-field'
        })

        self.fields['category'].widget.attrs.update({
            'class': 'form-select',
            'id': 'product-category-field'
        })

        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00',
            'id': 'product-price-field'
        })

        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png',
            'id': 'product-image-field'
        })

        # Настройка поля статуса публикации
        self.fields['publication_status'].widget.attrs.update({
            'class': 'form-select',
            'id': 'product-status-field'
        })

        # Ограничиваем выбор статуса в зависимости от прав пользователя
        if self.user:
            if not self.user.has_perm('catalog.can_moderate_products'):
                # Обычные пользователи могут выбирать только между черновиком и отправкой на модерацию
                self.fields['publication_status'].choices = [
                    ('draft', 'Черновик'),
                    ('pending', 'На модерации'),
                ]
                # По умолчанию ставим черновик для новых товаров
                if not self.instance.pk:
                    self.fields['publication_status'].initial = 'draft'

        # Проверяем, есть ли категории в базе данных
        if not Category.objects.exists():
            # Если категорий нет, показываем пустой queryset и добавляем подсказку
            self.fields['category'].queryset = Category.objects.none()
            self.fields['category'].help_text = (
                'Категории не найдены. Сначала создайте категории в админ-панели.'
            )

        # Делаем поля обязательными визуально
        required_fields = ['name', 'category', 'price']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['required'] = True

    def clean_name(self):
        """
        Валидация названия товара.

        Проверяет:
        - Минимальную длину (3 символа)
        - Отсутствие запрещенных слов
        - Что название не состоит только из цифр
        """
        name = self.cleaned_data.get('name')

        if not name:
            return name

        # Удаляем лишние пробелы
        name = name.strip()

        # Проверяем минимальную длину
        if len(name) < 3:
            raise ValidationError(
                'Название товара должно содержать минимум 3 символа.'
            )

        # Проверяем, не состоит ли название только из цифр
        if name.isdigit():
            raise ValidationError(
                'Название товара не может состоять только из цифр.'
            )

        # Проверяем на запрещенные слова (в любом регистре)
        name_lower = name.lower()
        found_forbidden_words = []

        for forbidden_word in self.FORBIDDEN_WORDS:
            if forbidden_word in name_lower:
                found_forbidden_words.append(forbidden_word)

        if found_forbidden_words:
            raise ValidationError(
                f'В названии товара обнаружены запрещенные слова: '
                f'{", ".join(found_forbidden_words)}. '
                f'Пожалуйста, измените название.'
            )

        return name

    def clean_description(self):
        """
        Валидация описания товара.

        Проверяет отсутствие запрещенных слов в описании.
        """
        description = self.cleaned_data.get('description')

        if not description:
            # Описание необязательно, поэтому возвращаем как есть
            return description

        # Удаляем лишние пробелы
        description = description.strip()

        # Проверяем на запрещенные слова (в любом регистре)
        description_lower = description.lower()
        found_forbidden_words = []

        for forbidden_word in self.FORBIDDEN_WORDS:
            if forbidden_word in description_lower:
                found_forbidden_words.append(forbidden_word)

        if found_forbidden_words:
            raise ValidationError(
                f'В описании товара обнаружены запрещенные слова: '
                f'{", ".join(found_forbidden_words)}. '
                f'Пожалуйста, измените описание.'
            )

        return description

    def clean_price(self):
        """
        Валидация цены товара.

        Проверяет:
        - Что цена не отрицательная
        - Что цена не превышает разумный максимум
        - Правильность формата (до 2 знаков после запятой)
        """
        price = self.cleaned_data.get('price')

        if price is None:
            raise ValidationError('Цена товара обязательна для заполнения.')

        # Проверяем, что цена не отрицательная
        if price < 0:
            raise ValidationError(
                'Цена товара не может быть отрицательной. '
                'Введите положительное число.'
            )

        # Проверяем, что цена не равна нулю
        if price == 0:
            raise ValidationError(
                'Цена товара не может быть равна нулю. '
                'Введите цену больше 0.'
            )

        # Проверяем максимальную цену (защита от ошибок ввода)
        if price > 999999.99:
            raise ValidationError(
                'Цена товара не может превышать 999,999.99 руб. '
                'Проверьте правильность ввода.'
            )

        return price

    def clean_image(self):
        """
        Валидация загружаемого изображения.

        Проверяет:
        - Формат файла (только JPEG, JPG, PNG)
        - Размер файла (не более 5 МБ)
        - Что файл действительно является изображением
        """
        image = self.cleaned_data.get('image')

        if not image:
            # Изображение необязательно
            return image

        # Проверяем размер файла
        if image.size > self.MAX_IMAGE_SIZE:
            size_mb = round(image.size / (1024 * 1024), 2)
            max_size_mb = round(self.MAX_IMAGE_SIZE / (1024 * 1024), 2)
            raise ValidationError(
                f'Размер изображения ({size_mb} МБ) превышает максимально '
                f'допустимый размер ({max_size_mb} МБ). '
                f'Пожалуйста, выберите файл меньшего размера.'
            )

        # Получаем расширение файла
        file_extension = os.path.splitext(image.name)[1].lower().lstrip('.')

        # Проверяем формат файла
        if file_extension not in self.ALLOWED_IMAGE_FORMATS:
            raise ValidationError(
                f'Неподдерживаемый формат изображения: {file_extension.upper()}. '
                f'Разрешенные форматы: {", ".join([f.upper() for f in self.ALLOWED_IMAGE_FORMATS])}.'
            )

        # Дополнительная проверка MIME-типа файла
        if hasattr(image, 'content_type'):
            allowed_mime_types = [
                'image/jpeg', 'image/jpg', 'image/png'
            ]
            if image.content_type not in allowed_mime_types:
                raise ValidationError(
                    'Загруженный файл не является изображением в допустимом формате. '
                    'Пожалуйста, выберите файл JPEG или PNG.'
                )

        return image

    def clean_publication_status(self):
        """Валидация статуса публикации."""
        status = self.cleaned_data.get('publication_status')

        # Если пользователь не модератор, проверяем ограничения
        if self.user and not self.user.has_perm('catalog.can_moderate_products'):
            allowed_statuses = ['draft', 'pending']
            if status not in allowed_statuses:
                raise ValidationError(
                    'Вы можете выбрать только "Черновик" или "На модерации".'
                )

        return status

    def clean(self):
        """
        Общая валидация формы.

        Проверяет комбинации полей и может добавить дополнительные проверки.
        """
        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        price = cleaned_data.get('price')

        # Дополнительная проверка: если товар дорогой, должно быть подробное описание
        if price and price > 50000:
            if not description or len(description.strip()) < 50:
                raise ValidationError(
                    'Для товаров стоимостью более 50,000 руб. необходимо '
                    'подробное описание (минимум 50 символов).'
                )

        # Проверяем, что название и описание не дублируют друг друга
        if name and description:
            if name.lower().strip() == description.lower().strip():
                raise ValidationError(
                    'Название и описание товара не должны полностью совпадать. '
                    'Добавьте в описание дополнительную информацию о товаре.'
                )

        return cleaned_data


class ProductModerationForm(forms.ModelForm):
    """
    Форма для модерации товаров (только для модераторов).
    """

    class Meta:
        model = Product
        fields = ['publication_status']
        widgets = {
            'publication_status': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publication_status'].label = 'Изменить статус на:'