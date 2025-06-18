from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

# Получаем нашу кастомную модель пользователя
User = get_user_model()


class CustomUserRegistrationForm(UserCreationForm):
    """
    Форма регистрации пользователя с дополнительными полями.

    Наследуется от UserCreationForm Django, которая уже содержит логику
    для создания пользователя и валидации паролей. Мы добавляем свои поля
    и улучшаем стилизацию.
    """

    # Переопределяем email как обязательное поле с валидацией
    email = forms.EmailField(
        required=True,
        max_length=254,
        help_text='Обязательное поле. Введите действующий адрес электронной почты.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autocomplete': 'email'
        })
    )

    # Дополнительные поля из нашей модели
    first_name = forms.CharField(
        required=False,
        max_length=150,
        help_text='Ваше имя (необязательно)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя',
            'autocomplete': 'given-name'
        })
    )

    last_name = forms.CharField(
        required=False,
        max_length=150,
        help_text='Ваша фамилия (необязательно)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия',
            'autocomplete': 'family-name'
        })
    )

    phone_number = forms.CharField(
        required=False,
        max_length=20,
        help_text='Контактный номер телефона (необязательно)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67',
            'autocomplete': 'tel'
        })
    )

    # Список стран для выбора (можно расширить)
    COUNTRY_CHOICES = [
        ('', 'Выберите страну'),
        ('RU', 'Россия'),
        ('BY', 'Беларусь'),
        ('KZ', 'Казахстан'),
        ('UA', 'Украина'),
        ('US', 'США'),
        ('DE', 'Германия'),
        ('FR', 'Франция'),
        ('CN', 'Китай'),
        ('OTHER', 'Другая'),
    ]

    country = forms.ChoiceField(
        required=False,
        choices=COUNTRY_CHOICES,
        help_text='Ваша страна (необязательно)',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Переопределяем поля паролей для красивой стилизации
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        }),
        help_text='Пароль должен содержать минимум 8 символов и не быть слишком простым.'
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        }),
        help_text='Введите тот же пароль еще раз для подтверждения.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'phone_number', 'country', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """
        Переопределяем инициализацию для добавления Bootstrap классов
        к полям, которые Django создает автоматически.
        """
        super().__init__(*args, **kwargs)

        # Добавляем стили к полю username
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'autocomplete': 'username'
        })
        self.fields['username'].help_text = (
            'Обязательное поле. Не более 150 символов. '
            'Только буквы, цифры и символы @/./+/-/_'
        )

    def clean_email(self):
        """
        Дополнительная валидация email - проверяем уникальность.

        Django автоматически проверяет формат email, но нам нужно
        убедиться, что такой email еще не зарегистрирован.
        """
        email = self.cleaned_data.get('email')
        if email:
            # Приводим к нижнему регистру для унификации
            email = email.lower()

            # Проверяем, не существует ли уже пользователь с таким email
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    'Пользователь с таким адресом электронной почты уже существует. '
                    'Попробуйте войти в систему или используйте другой email.'
                )
        return email

    def clean_phone_number(self):
        """
        Валидация номера телефона - проверяем формат.
        """
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Удаляем все пробелы, дефисы и скобки
            cleaned_phone = re.sub(r'[^\d+]', '', phone)

            # Проверяем базовый формат (начинается с + или цифры, длина 10-15 символов)
            if not re.match(r'^(\+\d{1,3})?\d{10,14}$', cleaned_phone):
                raise ValidationError(
                    'Введите корректный номер телефона. '
                    'Примеры: +7 999 123-45-67, 8 (999) 123-45-67'
                )
            return cleaned_phone
        return phone

    def clean_username(self):
        """
        Дополнительная валидация имени пользователя.
        """
        username = self.cleaned_data.get('username')
        if username:
            # Проверяем, что username не является email адресом
            if '@' in username:
                raise ValidationError(
                    'Имя пользователя не может содержать символ @. '
                    'Используйте уникальное имя без символа @.'
                )

            # Проверяем минимальную длину
            if len(username) < 3:
                raise ValidationError(
                    'Имя пользователя должно содержать минимум 3 символа.'
                )
        return username

    def save(self, commit=True):
        """
        Переопределяем сохранение для установки email в нижнем регистре
        и других дополнительных операций.
        """
        user = super().save(commit=False)

        # Унифицируем email к нижнему регистру
        user.email = self.cleaned_data['email'].lower()

        # Сохраняем пользователя в базе данных если commit=True
        if commit:
            user.save()

        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Кастомная форма входа в систему.

    Наследуется от AuthenticationForm Django и добавляет красивую стилизацию
    Bootstrap. Также позволяет входить как по username, так и по email.
    """

    # Переопределяем поле username для поддержки email
    username = forms.CharField(
        label='Email или имя пользователя',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email или имя пользователя',
            'autocomplete': 'username',
            'autofocus': True  # Автофокус на первом поле
        })
    )

    # Переопределяем поле пароля
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password'
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        Инициализация формы с дополнительными настройками.
        """
        super().__init__(request, *args, **kwargs)

        # Убираем стандартные help_text, они нам не нужны на форме входа
        self.fields['username'].help_text = None
        self.fields['password'].help_text = None

    def clean_username(self):
        """
        Переопределяем валидацию username для поддержки входа по email.

        Если пользователь ввел email, ищем соответствующий username.
        """
        username_or_email = self.cleaned_data.get('username')

        if username_or_email:
            # Проверяем, введен ли email
            if '@' in username_or_email:
                try:
                    # Ищем пользователя по email и возвращаем его username
                    user = User.objects.get(email=username_or_email.lower())
                    return user.username
                except User.DoesNotExist:
                    # Если пользователь не найден, Django сам выдаст ошибку
                    # в методе clean() родительского класса
                    pass

        return username_or_email


class UserProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.

    Позволяет пользователю обновлять свою личную информацию
    после регистрации, кроме критически важных полей как email и username.
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'country', 'avatar')

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваша фамилия'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем выборы стран для поля country
        self.fields['country'].choices = CustomUserRegistrationForm.COUNTRY_CHOICES

        # Добавляем подсказки
        self.fields['avatar'].help_text = 'Загрузите изображение для вашего профиля (JPG, PNG)'
        self.fields['phone_number'].help_text = 'Контактный номер телефона'

    def clean_phone_number(self):
        """Переиспользуем валидацию телефона из формы регистрации."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^(\+\d{1,3})?\d{10,14}$', cleaned_phone):
                raise ValidationError(
                    'Введите корректный номер телефона. '
                    'Примеры: +7 999 123-45-67, 8 (999) 123-45-67'
                )
            return cleaned_phone
        return phone