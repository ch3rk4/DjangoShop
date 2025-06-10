from django.views.generic import ListView, DetailView, TemplateView
from .models import Product


class HomeView(ListView):
    """
    Главная страница с отображением товаров.
    """
    model = Product
    template_name = 'catalog/index.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """
        Определяет, какие товары показывать.
        """
        queryset = Product.objects.all()

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
        )[:4]  # 4 похожих товара

        return context


class ContactView(TemplateView):
    """
    Страница контактов
    """
    template_name = 'catalog/contact.html'

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