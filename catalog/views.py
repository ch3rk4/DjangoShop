from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """
    Главная страница с отображением товаров.

    ОБЩЕДОСТУПНАЯ - любой посетитель может просматривать товары.
    """
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """
        Определяет, какие товары показывать.
        Показываем только опубликованные товары для обычных пользователей.
        """
        queryset = Product.objects.select_related('category', 'owner').all()

        # Фильтруем по статусу публикации
        if not self.request.user.is_authenticated or not self.request.user.has_perm('catalog.can_moderate_product'):
            # Обычные пользователи видят только опубликованные товары
            queryset = queryset.filter(publication_status='published')

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Каталог товаров'
        context['total_products'] = Product.objects.filter(publication_status='published').count()

        # Для совместимости со старыми шаблонами
        context['latest_products_count'] = context['total_products']

        # Добавляем информацию о поиске
        search_query = self.request.GET.get('search')
        if search_query:
            context['search_query'] = search_query
            context['search_results_count'] = context['products'].count()

        return context


class ProductDetailView(DetailView):
    """
    Страница детального просмотра товара.

    ОБЩЕДОСТУПНАЯ - любой может посмотреть на товар детально.
    """
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Проверяем права на просмотр товара."""
        queryset = Product.objects.select_related('category', 'owner')

        # Если пользователь не модератор, показываем только опубликованные
        if not self.request.user.is_authenticated or not self.request.user.has_perm('catalog.can_moderate_product'):
            queryset = queryset.filter(publication_status='published')

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию о товаре."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Товар: {self.object.name}'

        # Добавляем связанные товары из той же категории
        context['related_products'] = Product.objects.exclude(
            pk=self.object.pk
        ).filter(
            category=self.object.category,
            publication_status='published'
        )[:4]  # 4 похожих товара

        # Проверяем права пользователя
        context['can_edit'] = self.object.can_be_edited_by(self.request.user)
        context['can_delete'] = self.object.can_be_deleted_by(self.request.user)

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    Страница создания нового товара.

    ТРЕБУЕТ АВТОРИЗАЦИИ - только зарегистрированные пользователи могут добавлять товары.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    success_url = reverse_lazy('catalog:home')

    # Настройки для LoginRequiredMixin
    login_url = '/users/login/'
    permission_denied_message = 'Для добавления товаров необходимо войти в систему'

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        Автоматически устанавливаем владельца товара.
        """
        # Устанавливаем владельца товара
        form.instance.owner = self.request.user

        # Если пользователь - модератор, можно сразу опубликовать
        if self.request.user.has_perm('catalog.can_moderate_product'):
            form.instance.publication_status = 'published'
        else:
            form.instance.publication_status = 'moderation'

        messages.success(
            self.request,
            f'Товар "{form.instance.name}" успешно добавлен! '
            f'{"Товар опубликован." if form.instance.publication_status == "published" else "Товар отправлен на модерацию."}'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавить товар'
        context['submit_text'] = 'Добавить товар'
        return context


class ContactView(TemplateView):
    """
    Страница контактов.

    ОБЩЕДОСТУПНАЯ - любой может посмотреть контактную информацию.
    """
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        """Добавляем контактную информацию."""
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Контакты',
            'company_name': 'Django Shop',
            'email': 'info@djangoshop.com',
            'phone': '+7 (123) 456-78-90',
            'address': 'г. Москва, ул. Примерная, д. 123',
            'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: выходной'
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Обработка отправки формы обратной связи.

        ОБЩЕДОСТУПНАЯ - любой может отправить сообщение.
        """
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Простая валидация
        if not all([name, email, message_text]):
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
            return self.get(request, *args, **kwargs)

        if len(message_text) < 10:
            messages.error(request, 'Сообщение должно содержать минимум 10 символов.')
            return self.get(request, *args, **kwargs)

        # Здесь можно добавить отправку email администратору
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            # Формируем тему письма
            email_subject = f'Новое сообщение с сайта от {name}'
            if subject:
                email_subject += f' (Тема: {subject})'

            # Формируем содержание
            email_message = f"""
Новое сообщение с сайта Django Shop:

От: {name}
Email: {email}
Тема: {subject or 'Не указана'}

Сообщение:
{message_text}

---
Отправлено: {request.META.get('REMOTE_ADDR')} в {timezone.now()}
            """

            # Отправляем письмо
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,  # Не показываем ошибки пользователю
            )

            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение успешно отправлено. '
                f'Мы свяжемся с вами в ближайшее время по адресу {email}.'
            )
        except Exception as e:
            # Логируем ошибку, но не показываем пользователю
            print(f"Ошибка отправки письма: {e}")
            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение принято к рассмотрению.'
            )

        # Перенаправляем на ту же страницу, чтобы избежать повторной отправки
        return self.get(request, *args, **kwargs)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Контроллер редактирования товара.

    ТРЕБУЕТ АВТОРИЗАЦИИ и проверки прав - только владелец или модератор.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, может ли пользователь редактировать товар."""
        product = self.get_object()
        return product.can_be_edited_by(self.request.user)

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'У вас нет прав для редактирования этого товара.')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def get_success_url(self):
        """Перенаправляем на страницу товара после редактирования."""
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Показываем сообщение об успешном обновлении."""
        messages.success(
            self.request,
            f'Товар "{form.instance.name}" успешно обновлен!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование: {self.object.name}'
        context['submit_text'] = 'Сохранить изменения'
        context['form_action'] = 'update'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Контроллер удаления товара.

    ТРЕБУЕТ АВТОРИЗАЦИИ и проверки прав - только владелец или модератор.
    """
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, может ли пользователь удалить товар."""
        product = self.get_object()
        return product.can_be_deleted_by(self.request.user)

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'У вас нет прав для удаления этого товара.')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def delete(self, request, *args, **kwargs):
        """Показываем сообщение об успешном удалении."""
        product_name = self.get_object().name
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Товар "{product_name}" успешно удален из каталога.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление товара: {self.object.name}'
        return context


class ProductModerationView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Контроллер для модерации товаров.

    Доступен только модераторам.
    """
    model = Product
    fields = ['publication_status']
    template_name = 'catalog/product_moderation.html'
    success_url = reverse_lazy('catalog:home')

    def test_func(self):
        """Проверяем права модератора."""
        return self.request.user.has_perm('catalog.can_change_product_status')

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'У вас нет прав модератора.')
        return redirect('catalog:home')

    def form_valid(self, form):
        """Обработка изменения статуса."""
        old_status = self.get_object().publication_status
        new_status = form.instance.publication_status

        if old_status != new_status:
            messages.success(
                self.request,
                f'Статус товара "{form.instance.name}" изменен с "{self.get_object().get_publication_status_display()}" на "{form.instance.get_publication_status_display()}"'
            )

        return super().form_valid(form)