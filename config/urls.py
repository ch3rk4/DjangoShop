from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # Главная страница и каталог товаров
    path('', include('catalog.urls')),

    # Все URL-ы блога начинаются с 'blogs/'
    # Требование задания - контроллеры должны быть зарегистрированы на адреса blogs/...
    path('blogs/', include('blog.urls')),
]

# В режиме разработки добавляем обслуживание медиафайлов
# В продакшене это будет делать веб-сервер (nginx, apache)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])