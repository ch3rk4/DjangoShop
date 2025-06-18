from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm, UserProfileForm

# Получаем нашу кастомную модель пользователя
User = get_user_model()


class CustomUserRegistrationView(CreateView):
    """
    Контроллер регистрации пользователя.
    """

    model = User
    form_class = CustomUserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:home')  # Куда перенаправить после регистрации

    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительную информацию в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Регистрация нового пользователя'
        context['submit_text'] = 'Зарегистрироваться'
        return context

    def form_valid(self, form):
        """
        Этот метод вызывается когда форма успешно прошла валидацию.
        """

        # Сначала сохраняем пользователя (вызываем родительский метод)
        response = super().form_valid(form)

        # Получаем созданного пользователя
        user = self.object

        # Автоматически входим пользователя в систему после регистрации
        # Это улучшает пользовательский опыт - не нужно вводить данные заново
        login(self.request, user)

        # Отправляем приветственное письмо
        self.send_welcome_email(user)

        # Показываем сообщение об успешной регистрации
        messages.success(
            self.request,
            f'Добро пожаловать, {user.get_full_name() or user.username}! '
            f'Ваш аккаунт успешно создан. На email {user.email} отправлено приветственное письмо.'
        )

        return response

    def send_welcome_email(self, user):
        """
        Отправляет приветственное письмо новому пользователю.

        Это важная часть пользовательского опыта - приветственное письмо
        подтверждает регистрацию и может содержать полезную информацию.
        """

        # Формируем тему письма
        subject = f'Добро пожаловать в Django Shop, {user.get_full_name() or user.username}!'

        # Формируем содержание письма
        message = f"""
Здравствуйте, {user.get_full_name() or user.username}!

Поздравляем с успешной регистрацией в интернет-магазине Django Shop!

Ваши данные для входа:
• Email: {user.email}
• Имя пользователя: {user.username}

Что вы можете делать:
• Просматривать каталог товаров
• Добавлять новые товары
• Читать и создавать статьи в блоге
• Редактировать свой профиль

Полезные ссылки:
• Главная страница: {self.request.build_absolute_uri('/')}
• Ваш профиль: {self.request.build_absolute_uri(reverse_lazy('users:profile'))}
• Добавить товар: {self.request.build_absolute_uri(reverse_lazy('catalog:add_product'))}

Если у вас есть вопросы, свяжитесь с нами через страницу контактов.

С наилучшими пожеланиями,
Команда Django Shop

---
Это автоматическое сообщение, пожалуйста, не отвечайте на него.
        """

        try:
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,  # Если письмо не отправится, будет ошибка
            )

            # Логируем успешную отправку для отладки
            print(f"✅ Приветственное письмо отправлено пользователю {user.email}")

        except Exception as e:
            # Если письмо не отправилось, логируем ошибку но не останавливаем регистрацию
            print(f"❌ Ошибка отправки приветственного письма для {user.email}: {e}")

            # Можно добавить уведомление администратору об ошибке
            messages.warning(
                self.request,
                'Регистрация прошла успешно, но возникла проблема с отправкой приветственного письма.'
            )


class CustomLoginView(LoginView):
    """
    Контроллер входа в систему.
    """

    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True  # Перенаправляем уже авторизованных пользователей

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Вход в систему'
        context['submit_text'] = 'Войти'
        return context

    def form_valid(self, form):
        """
        Вызывается при успешной аутентификации.
        """

        # Получаем пользователя до вызова родительского метода
        user = form.get_user()

        # Вызываем родительский метод (выполняет вход)
        response = super().form_valid(form)

        # Показываем приветственное сообщение
        messages.success(
            self.request,
            f'Добро пожаловать, {user.get_full_name() or user.username}! '
            f'Вы успешно вошли в систему.'
        )

        # Логируем событие для администратора
        print(f"👤 Пользователь {user.username} ({user.email}) вошел в систему")

        return response

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного входа.
        """

        # Проверяем, есть ли параметр 'next' в URL
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        # Используем настройку из settings.py или главную страницу
        return getattr(settings, 'LOGIN_REDIRECT_URL', '/')


class CustomLogoutView(LogoutView):
    """
    Контроллер выхода из системы.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Вызывается перед обработкой запроса.
        """

        # Сохраняем имя пользователя до выхода
        if request.user.is_authenticated:
            self.user_name = request.user.get_full_name() or request.user.username
            print(f"👋 Пользователь {request.user.username} вышел из системы")
        else:
            self.user_name = None

        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        """
        Определяет URL для перенаправления после выхода.
        """

        # Добавляем сообщение о выходе если пользователь был авторизован
        if hasattr(self, 'user_name') and self.user_name:
            messages.info(
                self.request,
                f'До свидания, {self.user_name}! Вы успешно вышли из системы.'
            )

        # Используем настройку из settings.py или главную страницу
        return getattr(settings, 'LOGOUT_REDIRECT_URL', '/')


class UserProfileView(LoginRequiredMixin, UpdateView):
    """
    Контроллер просмотра и редактирования профиля пользователя.
    """

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        """
        Возвращает объект для редактирования.
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        """Добавляем информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Мой профиль'
        context['submit_text'] = 'Сохранить изменения'
        return context

    def form_valid(self, form):
        """Вызывается при успешном сохранении профиля."""

        response = super().form_valid(form)

        messages.success(
            self.request,
            'Ваш профиль успешно обновлен!'
        )

        return response


def home_view(request):
    """
    Простая функция-контроллер для главной страницы пользователей.
    """

    context = {
        'page_title': 'Добро пожаловать!',
        'total_users': User.objects.count(),
    }

    # Если пользователь авторизован, добавляем персональную информацию
    if request.user.is_authenticated:
        context['user_products_count'] = request.user.products.count() if hasattr(request.user, 'products') else 0

    return render(request, 'users/home.html', context)