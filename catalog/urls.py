from django.urls import path
from .views import HomeView, ProductDetailView, ContactView

# Пространство имен приложения для избежания конфликтов URL
app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога
    path('', HomeView.as_view(), name='home'),

    # Детальная страница товара
    # <int:pk> означает, что ожидаем целое число (ID товара)
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Страница контактов
    path('contact/', ContactView.as_view(), name='contact'),
]