from django.urls import path
from .views import (
    HomeView, ProductDetailView, ContactView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, ProductUnpublishView,
    CategoryProductsView
)

# Пространство имен приложения для избежания конфликтов URL
app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога
    path('', HomeView.as_view(), name='home'),

    # Детальная страница товара
    # <int:pk> означает, что ожидаем целое число (ID товара)
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Страница контактов
    path('contacts/', ContactView.as_view(), name='contacts'),

    # Страница добавления товара
    path('add-product/', ProductCreateView.as_view(), name='add_product'),

    # НОВЫЕ URL для управления товарами

    # Редактирование товара
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),

    # Удаление товара
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Снятие товара с публикации (для модераторов)
    path('product/<int:pk>/unpublish/', ProductUnpublishView.as_view(), name='product_unpublish'),

    # Товары по категориям
    path('category/<int:category_id>/', CategoryProductsView.as_view(), name='category_products'),
]