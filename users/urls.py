from django.urls import path
from .views import (
    CustomUserRegistrationView,
    CustomLoginView,
    CustomLogoutView,
    UserProfileView,
    home_view
)

# Пространство имен для URL-ов пользователей
# Это позволяет избежать конфликтов с URL-ами других приложений
app_name = 'users'

urlpatterns = [
    # Главная страница пользователей
    # URL: /users/
    # Показывает приветственную страницу или дашборд
    path('', home_view, name='home'),

    # Регистрация нового пользователя
    # URL: /users/register/
    # Показывает форму регистрации и обрабатывает создание аккаунта
    path('register/', CustomUserRegistrationView.as_view(), name='register'),

    # Вход в систему
    # URL: /users/login/
    # Показывает форму входа и обрабатывает аутентификацию
    path('login/', CustomLoginView.as_view(), name='login'),

    # Выход из системы
    # URL: /users/logout/
    # Выполняет выход пользователя и перенаправляет на главную
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Профиль пользователя
    # URL: /users/profile/
    # Показывает и позволяет редактировать профиль текущего пользователя
    # Доступен только авторизованным пользователям
    path('profile/', UserProfileView.as_view(), name='profile'),
]

"""
Объяснение структуры URL-ов:

1. Пространство имен (app_name = 'users'):
   Позволяет обращаться к URL-ам как 'users:login', 'users:register' и т.д.
   Это предотвращает конфликты, если в других приложениях есть URL с именем 'login'

2. Паттерны URL-ов:
   - '' (пустая строка) соответствует /users/
   - 'register/' соответствует /users/register/
   - 'login/' соответствует /users/login/
   - и т.д.

3. Использование .as_view():
   Классы-контроллеры нужно "превратить" в функции с помощью as_view()
   Функции-контроллеры (home_view) используются напрямую

4. Имена URL-ов (name=):
   Позволяют обращаться к URL-ам в шаблонах и коде:
   {% url 'users:login' %} вместо жестко заданного /users/login/

Примеры использования в шаблонах:
- <a href="{% url 'users:register' %}">Регистрация</a>
- <a href="{% url 'users:login' %}">Вход</a>
- <a href="{% url 'users:profile' %}">Мой профиль</a>

Примеры использования в коде:
- reverse('users:login')
- reverse_lazy('users:profile')
"""