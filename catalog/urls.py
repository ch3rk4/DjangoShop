from django.urls import path
from .views import (
    HomeView, ProductDetailView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, ContactView
)

# Пространство имен приложения для избежания конфликтов URL
# Это позволяет нам использовать 'catalog:home' вместо просто 'home'
app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога - список всех товаров
    # URL: / (корень сайта)
    # Представление: HomeView (ListView для отображения товаров с пагинацией)
    path('', HomeView.as_view(), name='home'),

    # Страница создания нового товара
    # URL: /products/create/
    # Представление: ProductCreateView (CreateView с формой ProductForm)
    path('products/create/', ProductCreateView.as_view(), name='product_create'),

    # Детальная страница товара
    # URL: /products/1/ (где 1 - это ID товара)
    # <int:pk> означает, что ожидаем целое число (primary key товара)
    # Представление: ProductDetailView (DetailView для показа одного товара)
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Страница редактирования товара
    # URL: /products/1/edit/ (где 1 - это ID товара)
    # Представление: ProductUpdateView (UpdateView с формой ProductForm)
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),

    # Страница подтверждения удаления товара
    # URL: /products/1/delete/ (где 1 - это ID товара)
    # Представление: ProductDeleteView (DeleteView с подтверждением)
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Страница контактов
    # URL: /contacts/
    # Представление: ContactView (TemplateView с формой обратной связи)
    path('contacts/', ContactView.as_view(), name='contacts'),

    # Совместимость со старыми URL (если они использовались)
    # URL: /contact/ (редирект на /contacts/)
    path('contact/', ContactView.as_view(), name='contact'),

    # Дополнительные URL для удобства (альтернативные пути)
    # URL: /add/ (короткий путь для добавления товара)
    path('add/', ProductCreateView.as_view(), name='add_product'),
]
