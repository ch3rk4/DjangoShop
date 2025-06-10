from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, Category
from .forms import ProductForm


def home(request):
    """
    Контроллер для отображения главной страницы с пагинацией.

    Теперь включает постраничное отображение товаров для лучшей навигации
    по большому каталогу товаров.
    """
    # Получаем все товары с оптимизированным запросом
    products_list = Product.objects.select_related('category').all()

    # Настройка пагинации - по 6 товаров на страницу
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # Дополнительное задание из ДЗ2: выводим последние 5 товаров в консоль
    latest_products = Product.objects.select_related('category').order_by('-created_at')[:5]

    print("=== ПОСЛЕДНИЕ 5 СОЗДАННЫХ ТОВАРОВ ===")
    for product in latest_products:
        print(f"ID: {product.id}")
        print(f"Название: {product.name}")
        print(f"Категория: {product.category.name}")
        print(f"Цена: {product.price} руб.")
        print(f"Создан: {product.created_at}")
        print("-" * 40)

    context = {
        'products': products,  # Теперь это объект Page с товарами
        'latest_products_count': latest_products.count(),
    }

    return render(request, 'catalog/home.html', context)


def product_detail(request, pk):
    """
    Контроллер для отображения детальной информации о товаре.

    Принимает первичный ключ товара (pk) и возвращает страницу
    с полной информацией о выбранном товаре.
    """
    # Получаем товар по первичному ключу или возвращаем 404
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk
    )

    context = {
        'product': product,
    }

    return render(request, 'catalog/product_detail.html', context)


def contacts(request):
    """
    Контроллер для отображения страницы контактов.

    Обрабатывает как GET-запросы для отображения формы,
    так и POST-запросы для обработки отправленных данных.
    """
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Простая валидация
        if name and email and message:
            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение успешно отправлено. '
                'Мы свяжемся с вами в ближайшее время.'
            )
        else:
            messages.error(request, 'Пожалуйста, заполните все поля формы.')

    return render(request, 'catalog/contacts.html')


def add_product(request):
    """
    Контроллер для добавления нового товара (дополнительное задание).

    Позволяет пользователям добавлять новые товары в каталог
    через веб-форму с валидацией данных.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем новый товар в базу данных
            product = form.save()
            messages.success(
                request,
                f'Товар "{product.name}" успешно добавлен в каталог!'
            )
            # Перенаправляем на страницу детального просмотра нового товара
            return HttpResponseRedirect(
                reverse('catalog:product_detail', args=[product.pk])
            )
        else:
            messages.error(
                request,
                'Пожалуйста, исправьте ошибки в форме.'
            )
    else:
        form = ProductForm()

    context = {
        'form': form,
    }

    return render(request, 'catalog/add_product.html', context)