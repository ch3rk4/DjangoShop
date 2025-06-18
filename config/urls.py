from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # Главная страница и каталог товаров
    path('', include('catalog.urls')),

    # НОВОЕ: Все URL-ы пользователей начинаются с 'users/'
    # Это включает регистрацию, вход, выход и профиль
    path('users/', include('users.urls')),

    # Все URL-ы блога начинаются с 'blogs/'
    # Требование задания - контроллеры должны быть зарегистрированы на адреса blogs/...
    path('blogs/', include('blog.urls')),
]

# В режиме разработки добавляем обслуживание медиафайлов
# В продакшене это будет делать веб-сервер (nginx, apache)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

"""
Структура URL-ов после добавления пользователей:

Каталог товаров:
- / - главная страница с товарами
- /product/1/ - страница товара
- /contacts/ - контакты
- /add-product/ - добавление товара

Пользователи:
- /users/ - главная пользователей
- /users/register/ - регистрация
- /users/login/ - вход
- /users/logout/ - выход
- /users/profile/ - профиль

Блог:
- /blogs/ - список статей
- /blogs/post/1/ - отдельная статья
- /blogs/create/ - создание статьи

Админка:
- /admin/ - административная панель

Это логичная и понятная структура, где каждое приложение имеет свой "район" в URL пространстве.
"""