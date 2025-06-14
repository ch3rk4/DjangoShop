from django.urls import path
from .views import (
    BlogListView, BlogDetailView, BlogCreateView,
    BlogUpdateView, BlogDeleteView
)

# Пространство имен для блога
app_name = 'blog'

urlpatterns = [
    # Главная страница блога - список всех статей
    path('', BlogListView.as_view(), name='list'),  # ИСПРАВЛЕНО: name='list'

    # Альтернативное имя для совместимости с шаблонами
    path('list/', BlogListView.as_view(), name='blog_list'),

    # Страница отдельной статьи
    path('post/<int:pk>/', BlogDetailView.as_view(), name='detail'),  # ИСПРАВЛЕНО: name='detail'

    # Создание новой статьи
    path('create/', BlogCreateView.as_view(), name='create'),  # ИСПРАВЛЕНО: name='create'

    # Редактирование существующей статьи
    path('post/<int:pk>/edit/', BlogUpdateView.as_view(), name='update'),  # ИСПРАВЛЕНО: name='update'

    # Удаление статьи
    path('post/<int:pk>/delete/', BlogDeleteView.as_view(), name='delete'),  # ИСПРАВЛЕНО: name='delete'

    # Дополнительные псевдонимы для совместимости с существующими шаблонами
    path('post/<int:pk>/detail/', BlogDetailView.as_view(), name='post_detail'),
    path('create-post/', BlogCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', BlogUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/remove/', BlogDeleteView.as_view(), name='post_delete'),
]