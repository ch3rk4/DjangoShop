from django.urls import path
from .views import (
    BlogListView, BlogDetailView, BlogCreateView,
    BlogUpdateView, BlogDeleteView
)

# Пространство имен для блога
app_name = 'blog'

urlpatterns = [
    # Главная страница блога - список всех статей
    path('', BlogListView.as_view(), name='blog_list'),

    # Страница отдельной статьи
    path('post/<int:pk>/', BlogDetailView.as_view(), name='post_detail'),

    # Создание новой статьи
    path('create/', BlogCreateView.as_view(), name='post_create'),

    # Редактирование существующей статьи
    path('post/<int:pk>/edit/', BlogUpdateView.as_view(), name='post_update'),

    # Удаление статьи
    path('post/<int:pk>/delete/', BlogDeleteView.as_view(), name='post_delete'),
]