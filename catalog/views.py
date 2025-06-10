from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """
    Главная страница с отображением товаров.

    Наследуется от ListView, что означает автоматическое создание
    пагинации и передачу списка объектов в шаблон.
    """
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 12  # Показываем по 12 товаров на странице

    def get_queryset(self):
        """
        Определяет, какие товары показывать на главной странице.

        Мы можем добавить здесь фильтрацию, поиск или сортировку.
        """
        # Получаем все товары, отсортированные по дате создания (новые первые)
        queryset = Product.objects.select_related('category').order_by('-created_at')

        # Добавляем возможность поиска через GET-параметр
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Это позволяет передать в шаблон любую дополнительную информацию,
        которая может понадобиться для отображения.
        """
        context = super().get_context_data(**kwargs)

        # Добавляем общую информацию о каталоге
        context['page_title'] = 'Каталог товаров'
        context['total_products'] = Product.objects.count()

        # Добавляем информацию о поиске
        search_query = self.request.GET.get('search')
        if search_query:
            context['search_query'] = search_query
            context['search_results_count'] = context['products'].count()

        # Добавляем последние добавленные товары для вывода в консоль
        latest_products = Product.objects.order_by('-created_at')[:5]
        context['latest_products_count'] = latest_products.count()

        # Выводим информацию в консоль для отладки
        print(f"📦 Показано товаров на странице: {len(context['products'])}")
        if latest_products.exists():
            print(f"🆕 Последние {latest_products.count()} товаров:")
            for product in latest_products:
                print(f"   • {product.name} - {product.price} руб.")

        return context


class ProductDetailView(DetailView):
    """
    Страница детального просмотра одного товара.

    DetailView автоматически получает объект по первичному ключу (pk)
    из URL и передает его в шаблон.
    """
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        """
        Получаем объект товара и добавляем оптимизацию запросов.
        """
        # Используем select_related для оптимизации запроса к базе данных
        # Это загружает связанную категорию в одном запросе
        return get_object_or_404(
            Product.objects.select_related('category'),
            pk=self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительную информацию о товаре.
        """
        context = super().get_context_data(**kwargs)
        product = self.object

        context['page_title'] = f'Товар: {product.name}'

        # Добавляем похожие товары из той же категории
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(pk=product.pk).order_by('?')[:4]  # 4 случайных товара

        return context


class ProductCreateView(CreateView):
    """
    Страница создания нового товара.

    CreateView автоматически обрабатывает GET (показ формы) и
    POST (сохранение данных) запросы.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.

        Здесь мы можем добавить дополнительную обработку
        перед сохранением объекта.
        """
        # Добавляем сообщение об успешном создании
        messages.success(
            self.request,
            f'Товар "{form.cleaned_data["name"]}" успешно создан!'
        )

        # Выводим информацию в консоль для отладки
        print(f"✅ Создан новый товар: {form.cleaned_data['name']}")

        # Отправляем уведомление админу (в продакшене можно настроить email)
        try:
            send_mail(
                subject='Новый товар добавлен в каталог',
                message=f'В каталог добавлен новый товар: {form.cleaned_data["name"]}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,  # Не прерываем выполнение при ошибке email
            )
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Вызывается при неуспешной валидации формы.

        Добавляем сообщение об ошибке для пользователя.
        """
        messages.error(
            self.request,
            'Пожалуйста, исправьте ошибки в форме и попробуйте снова.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию для шаблона создания товара.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавление нового товара'
        context['form_action'] = 'create'
        context['submit_text'] = 'Создать товар'
        return context


class ProductUpdateView(UpdateView):
    """
    Страница редактирования существующего товара.

    UpdateView автоматически загружает существующий объект
    и заполняет форму его данными.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного редактирования.

        Перенаправляем пользователя на страницу отредактированного товара.
        """
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """
        Обработка успешной валидации при редактировании.
        """
        messages.success(
            self.request,
            f'Товар "{form.cleaned_data["name"]}" успешно обновлен!'
        )

        print(f"✏️ Обновлен товар: {form.cleaned_data['name']}")

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обработка ошибок валидации при редактировании.
        """
        messages.error(
            self.request,
            'Не удалось сохранить изменения. Проверьте правильность заполнения полей.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию для шаблона редактирования товара.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование товара: {self.object.name}'
        context['form_action'] = 'update'
        context['submit_text'] = 'Сохранить изменения'
        return context


class ProductDeleteView(DeleteView):
    """
    Страница подтверждения удаления товара.

    DeleteView показывает страницу подтверждения при GET-запросе
    и удаляет объект при POST-запросе.
    """
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def delete(self, request, *args, **kwargs):
        """
        Переопределяем метод удаления для добавления сообщения.
        """
        # Сохраняем название товара перед удалением
        product_name = self.get_object().name

        # Добавляем сообщение об успешном удалении
        messages.success(
            request,
            f'Товар "{product_name}" успешно удален из каталога.'
        )

        print(f"🗑️ Удален товар: {product_name}")

        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию для шаблона подтверждения удаления.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление товара: {self.object.name}'
        return context


class ContactView(TemplateView):
    """
    Страница контактов.

    TemplateView используется для статических страниц,
    которые не работают с моделями.
    """
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        """
        Добавляем контактную информацию.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Контакты',
            'company_name': 'Django Shop',
            'email': 'info@djangoshop.com',
            'phone': '+7 (495) 123-45-67',
            'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
            'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00'
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Обработка отправки формы обратной связи.

        Этот метод вызывается при POST-запросе на страницу контактов.
        """
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        # Простая валидация
        errors = []
        if not name:
            errors.append('Имя обязательно для заполнения')
        if not email:
            errors.append('Email обязателен для заполнения')
        if not message or len(message) < 10:
            errors.append('Сообщение должно содержать минимум 10 символов')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Отправляем email (в продакшене)
            try:
                send_mail(
                    subject=f'Обращение с сайта: {subject or "Без темы"}',
                    message=f'От: {name} ({email})\n\nСообщение:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    'Ваше сообщение успешно отправлено! Мы ответим в ближайшее время.'
                )
                print(f"📧 Получено сообщение от {name} ({email})")
            except Exception as e:
                messages.error(
                    request,
                    'Произошла ошибка при отправке сообщения. Попробуйте позже.'
                )
                print(f"❌ Ошибка отправки email: {e}")

        # Возвращаем обратно на страницу контактов
        return self.get(request, *args, **kwargs)