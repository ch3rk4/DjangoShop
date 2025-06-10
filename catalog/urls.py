from django.urls import path
from . import views

# Пространство имен для приложения catalog
# Это позволяет нам использовать 'catalog:home' вместо просто 'home'
# что очень полезно в больших проектах с множеством приложений
app_name = 'catalog'

urlpatterns = [
    # Главная страница - отображает список всех товаров с пагинацией
    # Паттерн: / (корневой URL)
    path('', views.home, name='home'),

    # Страница детального просмотра товара - новое в ДЗ3
    # Паттерн: /product/1/ где 1 это pk (первичный ключ) товара
    # <int:pk> означает, что Django ожидает целое число и передаст его как параметр pk
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Страница контактов - уже была в предыдущих заданиях
    # Паттерн: /contacts/
    path('contacts/', views.contacts, name='contacts'),

    # Страница добавления нового товара - дополнительное задание
    # Паттерн: /add-product/
    path('add-product/', views.add_product, name='add_product'),
]
