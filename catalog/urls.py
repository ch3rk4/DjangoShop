from django.urls import path
from .views import HomeView, ProductDetailView, ContactView, ProductCreateView

# Пространство имен приложения для избежания конфликтов URL
app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога
    path('', HomeView.as_view(), name='home'),

    # Детальная страница товара
    # <int:pk> означает, что ожидаем целое число (ID товара)
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Страница контактов - ИСПРАВЛЕНО: было contact/, стало contacts/
    path('contacts/', ContactView.as_view(), name='contacts'),

    # Страница добавления товара - ДОБАВЛЕНО: недостающий URL
    path('add-product/', ProductCreateView.as_view(), name='add_product'),
]