"""
Django settings for config project.
Исправленная версия с правильными настройками для пользователей.
"""

import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# БЕЗОПАСНОСТЬ: Секретный ключ для продакшена должен храниться в переменных окружения
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# БЕЗОПАСНОСТЬ: Не используйте DEBUG=True в продакшене!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Разрешенные хосты для подключения
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Приложения Django
INSTALLED_APPS = [
    # Встроенные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Наши кастомные приложения
    'users',    # Пользователи и аутентификация
    'catalog',  # Каталог товаров
    'blog',     # Блог
]

# Промежуточное ПО (middleware) - обрабатывает запросы и ответы
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ИСПРАВЛЕНО: Правильный путь к корневому URL-конфигу
ROOT_URLCONF = 'config.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Папка с общими шаблонами
        'APP_DIRS': True,  # Автоматический поиск шаблонов в приложениях
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'users.User'
DATABASE_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')

if DATABASE_ENGINE == 'django.db.backends.postgresql':
    # Настройки для PostgreSQL (для продакшена)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'djangoshop_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'charset': 'utf8',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Валидаторы паролей для безопасности
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# URL для перенаправления после успешного входа
LOGIN_REDIRECT_URL = '/'  # Главная страница каталога

# URL для перенаправления после выхода
LOGOUT_REDIRECT_URL = '/'  # Главная страница каталога

# URL страницы входа (куда перенаправлять неавторизованных пользователей)
LOGIN_URL = '/users/login/'

# Настройки локализации
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Настройки статических файлов (CSS, JavaScript, изображения)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Папка для статических файлов разработки
]
# В продакшене добавьте STATIC_ROOT для collectstatic

# Настройки медиафайлов (загружаемые пользователями файлы)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Поле по умолчанию для автоинкрементных ключей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки отправки email
# Для разработки используем консольный бэкенд (письма выводятся в терминал)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@djangoshop.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@djangoshop.com')

if not DEBUG:
    # Используйте HTTPS в продакшене
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Защита сессий
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True