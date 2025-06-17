from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Product
from .forms import ProductForm


class HomeView(ListView):
    """
    Главная страница с отображением товаров.
    """
    model = Product
    template_name = 'catalog/home.html'  # ИСПРАВЛЕНО: было index.html
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """
        Определяет, какие товары показывать.
        """
        queryset = Product.objects.select_related('category').all()

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
        context['total_products'] = Product.objects.count()

        # Для совместимости со старыми шаблонами
        context['latest_products_count'] = context['total_products']

        return context


class ProductDetailView(DetailView):
    """
    Страница детального просмотра товара.
    """
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию о товаре."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Товар: {self.object.name}'

        # Можно добавить связанные товары, отзывы и т.д.
        context['related_products'] = Product.objects.exclude(
            pk=self.object.pk
        ).filter(category=self.object.category)[:4]  # 4 похожих товара

        return context


class ProductCreateView(CreateView):
    """
    Страница создания нового товара.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        """
        messages.success(self.request, 'Товар успешно добавлен!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавить товар'
        return context


class ContactView(TemplateView):
    """
    Страница контактов
    """
    template_name = 'catalog/contacts.html'  # ИСПРАВЛЕНО: было contact.html

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