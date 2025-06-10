from django.shortcuts import render
from django.contrib import messages
from .models import Product


def home(request):
    """
    Контроллер для отображения главной страницы.

    Теперь получаем реальные товары из базы данных и выводим
    последние 5 созданных товаров в консоль (дополнительное задание).
    """
    # Получаем все товары для отображения на главной странице
    products = Product.objects.select_related('category').all()

    # Дополнительное задание: выводим последние 5 товаров в консоль
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
        'products': products,
        'latest_products_count': latest_products.count(),
    }

    return render(request, 'catalog/home.html', context)


def contacts(request):
    """
    Контроллер для отображения страницы контактов.

    В дополнительном задании здесь будет модель для хранения
    контактных данных и вывод данных из админки.
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