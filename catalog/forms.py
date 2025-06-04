from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Форма для создания и редактирования товаров.

    Эта форма использует ModelForm, что означает автоматическое создание
    полей на основе модели Product. Мы также добавляем дополнительные
    настройки для улучшения пользовательского опыта.
    """

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'image']

        # Настраиваем виджеты для лучшего отображения в HTML
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название товара'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите товар подробно'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

        # Переопределяем подписи для полей
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'category': 'Категория',
            'price': 'Цена (руб.)',
            'image': 'Изображение товара'
        }

        # Добавляем текст помощи для полей
        help_texts = {
            'name': 'Краткое и понятное название товара',
            'description': 'Подробное описание товара, его характеристики и преимущества',
            'price': 'Цена товара в рублях (например: 1500.00)',
            'image': 'Загрузите качественное изображение товара (форматы: JPG, PNG)'
        }

    def clean_price(self):
        """
        Дополнительная валидация цены.

        Эта функция проверяет, что цена положительная и не слишком большая.
        Django автоматически вызывает методы clean_<field_name> для валидации.
        """
        price = self.cleaned_data.get('price')

        if price is not None:
            if price <= 0:
                raise forms.ValidationError(
                    'Цена должна быть больше нуля.'
                )
            if price > 999999.99:
                raise forms.ValidationError(
                    'Цена не может превышать 999,999.99 руб.'
                )

        return price

    def clean_name(self):
        """
        Дополнительная валидация названия товара.

        Проверяем, что название не состоит только из пробелов
        и имеет разумную длину.
        """
        name = self.cleaned_data.get('name')

        if name:
            # Удаляем лишние пробелы
            name = name.strip()

            if len(name) < 3:
                raise forms.ValidationError(
                    'Название товара должно содержать минимум 3 символа.'
                )

            # Проверяем, не состоит ли название только из цифр
            if name.isdigit():
                raise forms.ValidationError(
                    'Название товара не может состоять только из цифр.'
                )

        return name