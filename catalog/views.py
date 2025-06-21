from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
import logging

from .models import Product, Category
from .forms import ProductForm, ProductModerationForm
from .services import (
    get_products_by_category,
    get_cached_product_list,
    get_popular_products,
    search_products,
    invalidate_products_cache,
    get_category_stats
)

# Настройка логирования для кеширования
logger = logging.getLogger('cache')


class HomeView(ListView):
    """
    Главная страница с отображением товаров.
    ОБЩЕДОСТУПНАЯ - любой посетитель может просматривать опубликованные товары.
    """
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """
        Определяет, какие товары показывать с использованием кеширования.
        """
        search_query = self.request.GET.get('search')

        if search_query:
            # Используем сервисную функцию для поиска
            return search_products(search_query, self.request.user)

        # Используем сервисную функцию для получения списка товаров
        filters = {}
        cache_key_suffix = "home"

        return get_cached_product_list(
            filters=filters,
            user=self.request.user,
            cache_key_suffix=cache_key_suffix
        )

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Каталог товаров'

        # Кешируем общую статистику
        stats_cache_key = "home_stats"

        if getattr(settings, 'CACHE_ENABLED', True):
            cached_stats = cache.get(stats_cache_key)
            if cached_stats:
                context.update(cached_stats)
                logger.info("Получена статистика главной страницы из кеша")
            else:
                stats = {
                    'total_products': Product.objects.filter(publication_status='published').count(),
                    'latest_products_count': context.get('total_products', 0),
                }
                cache.set(stats_cache_key, stats, 300)  # 5 минут
                context.update(stats)
                logger.info("Статистика главной страницы закеширована")
        else:
            context['total_products'] = Product.objects.filter(publication_status='published').count()
            context['latest_products_count'] = context['total_products']

        # Добавляем информацию о поиске
        search_query = self.request.GET.get('search')
        if search_query:
            context['search_query'] = search_query
            context['search_results_count'] = len(context['products'])

        return context


@method_decorator(cache_page(900), name='dispatch')  # 15 минут кеширования
class ProductDetailView(DetailView):
    """
    Страница детального просмотра товара.
    ОБЩЕДОСТУПНАЯ - любой может посмотреть на опубликованные товары.
    Кешируется на 15 минут.
    """
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Определяем доступные товары в зависимости от прав пользователя."""
        queryset = Product.objects.select_related('category', 'owner')

        # Модераторы и владельцы могут видеть все товары
        if (self.request.user.is_authenticated and
                (self.request.user.has_perm('catalog.can_moderate_products') or
                 queryset.filter(owner=self.request.user).exists())):
            return queryset

        # Обычные пользователи видят только опубликованные
        return queryset.filter(publication_status='published')

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию о товаре."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Товар: {self.object.name}'

        # Кешируем связанные товары
        related_cache_key = f"related_products_{self.object.category.pk}_{self.object.pk}"

        if getattr(settings, 'CACHE_ENABLED', True):
            related_products = cache.get(related_cache_key)
            if related_products is None:
                related_products = list(Product.objects.exclude(
                    pk=self.object.pk
                ).filter(
                    category=self.object.category,
                    publication_status='published'
                ).select_related('category', 'owner')[:4])

                cache.set(related_cache_key, related_products, 600)  # 10 минут
                logger.info(f"Кешированы связанные товары для продукта {self.object.pk}")
        else:
            related_products = Product.objects.exclude(
                pk=self.object.pk
            ).filter(
                category=self.object.category,
                publication_status='published'
            )[:4]

        context['related_products'] = related_products
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

    def get_form_kwargs(self):
        """Передаем пользователя в форму."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        Автоматически устанавливаем владельца товара.
        """
        # Устанавливаем владельца товара
        form.instance.owner = self.request.user

        response = super().form_valid(form)

        # Инвалидируем кеш товаров после создания
        invalidate_products_cache(form.instance.category.pk)

        messages.success(
            self.request,
            f'Товар "{form.instance.name}" успешно добавлен! '
            f'Статус: {form.instance.get_publication_status_display()}'
        )
        return response

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавить товар'
        context['submit_text'] = 'Добавить товар'
        return context


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Контроллер редактирования товара.
    ТРЕБУЕТ АВТОРИЗАЦИИ и проверки прав - только владелец или модератор может редактировать.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, может ли пользователь редактировать товар."""
        product = self.get_object()
        return product.can_be_edited_by(self.request.user)

    def get_form_kwargs(self):
        """Передаем пользователя в форму."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Перенаправляем на страницу товара после редактирования."""
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Показываем сообщение об успешном обновлении."""
        response = super().form_valid(form)

        # Инвалидируем кеш товаров после обновления
        invalidate_products_cache(form.instance.category.pk)

        messages.success(
            self.request,
            f'Товар "{form.instance.name}" успешно обновлен!'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование: {self.object.name}'
        context['submit_text'] = 'Сохранить изменения'
        context['form_action'] = 'update'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Контроллер удаления товара.
    ТРЕБУЕТ АВТОРИЗАЦИИ и проверки прав - только владелец или модератор продуктов может удалять.
    """
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, может ли пользователь удалить товар."""
        product = self.get_object()
        return product.can_be_deleted_by(self.request.user)

    def delete(self, request, *args, **kwargs):
        """Показываем сообщение об успешном удалении."""
        product = self.get_object()
        product_name = product.name
        category_id = product.category.pk

        response = super().delete(request, *args, **kwargs)

        # Инвалидируем кеш товаров после удаления
        invalidate_products_cache(category_id)

        messages.success(
            request,
            f'Товар "{product_name}" успешно удален из каталога.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление товара: {self.object.name}'
        return context


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Контроллер для снятия товара с публикации.
    Доступен только модераторам с соответствующими правами.
    """
    model = Product
    form_class = ProductModerationForm
    template_name = 'catalog/product_unpublish.html'
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем права на снятие с публикации."""
        return self.request.user.has_perm('catalog.can_unpublish_product')

    def form_valid(self, form):
        """Обрабатываем успешное изменение статуса."""
        old_status = self.object.publication_status
        response = super().form_valid(form)
        new_status = form.cleaned_data['publication_status']

        # Инвалидируем кеш товаров после изменения статуса
        invalidate_products_cache(self.object.category.pk)

        messages.success(
            self.request,
            f'Статус товара "{self.object.name}" изменен с '
            f'"{dict(Product.PUBLICATION_STATUS_CHOICES)[old_status]}" на "{dict(Product.PUBLICATION_STATUS_CHOICES)[new_status]}"'
        )

        return response

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class CategoryProductsView(ListView):
    """
    Страница товаров определенной категории с использованием сервисной функции.
    """
    model = Product
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Получаем товары определенной категории через сервисную функцию."""
        self.category = get_object_or_404(Category, pk=self.kwargs['category_id'])

        return get_products_by_category(
            category_id=self.category.pk,
            user=self.request.user,
            include_unpublished=False
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f'Товары в категории: {self.category.name}'

        # Добавляем статистику категории
        context['category_stats'] = get_category_stats(self.category.pk)

        return context


class PopularProductsView(ListView):
    """
    НОВОЕ: Страница популярных товаров.
    """
    template_name = 'catalog/popular_products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        """Получаем популярные товары через сервисную функцию."""
        limit = self.request.GET.get('limit', 20)
        try:
            limit = int(limit)
            if limit > 100:  # Ограничиваем максимум
                limit = 100
        except (ValueError, TypeError):
            limit = 20

        return get_popular_products(limit=limit)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Популярные товары'
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