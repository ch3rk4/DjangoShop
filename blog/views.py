from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import BlogPost


class BlogListView(ListView):
    """
    Страница со списком всех блоговых записей.

    ОБЩЕДОСТУПНАЯ - любой посетитель может читать статьи блога.
    Это как читальный зал библиотеки - открыт для всех.
    """
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6  # Показываем по 6 статей на странице

    def get_queryset(self):
        """
        Фильтруем только опубликованные статьи для обычных пользователей.
        Контент-менеджеры могут видеть все статьи.
        """
        queryset = BlogPost.objects.all().order_by('-created_date')

        # Показываем только опубликованные статьи обычным пользователям
        if not (self.request.user.is_authenticated and
                self.request.user.groups.filter(name='Контент-менеджер').exists()):
            queryset = queryset.filter(is_published=True)

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Блог'
        context['total_posts'] = self.get_queryset().count()
        return context


class BlogDetailView(DetailView):
    """
    Страница детального просмотра одной статьи.

    ОБЩЕДОСТУПНАЯ - любой может прочитать опубликованную статью.
    """
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        """
        Определяем доступные статьи в зависимости от прав пользователя.
        """
        queryset = BlogPost.objects.all()

        # Контент-менеджеры могут видеть все статьи
        if (self.request.user.is_authenticated and
                self.request.user.groups.filter(name='Контент-менеджер').exists()):
            return queryset

        # Обычные пользователи видят только опубликованные
        return queryset.filter(is_published=True)

    def get_object(self, queryset=None):
        """
        Переопределяем получение объекта для увеличения счетчика просмотров.
        """
        # Сначала получаем объект стандартным способом
        obj = super().get_object(queryset)

        # Увеличиваем счетчик просмотров только для опубликованных статей
        if obj.is_published:
            old_views_count = obj.views_count
            obj.views_count += 1
            obj.save(update_fields=['views_count'])  # Обновляем только это поле

            # Проверяем, достигли ли ровно 100 просмотров
            if old_views_count < 100 and obj.views_count >= 100:
                self.send_congratulation_email(obj)

        return obj

    def send_congratulation_email(self, post):
        """
        Отправляет поздравительное письмо при достижении 100 просмотров.
        """
        subject = f'🎉 Поздравляем! Статья "{post.title}" достигла 100 просмотров!'

        message = f"""
        Отличные новости! 

        Ваша статья "{post.title}" только что достигла важной отметки в 100 просмотров!

        Подробности:
        📅 Дата создания: {post.created_date.strftime('%d.%m.%Y в %H:%M')}
        👀 Текущее количество просмотров: {post.views_count}
        📝 Статус: {'Опубликована' if post.is_published else 'Черновик'}

        Продолжайте создавать интересный контент!

        С уважением,
        Команда Django Shop Blog
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            print(f"📧 Отправлено поздравление за статью '{post.title}'")
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")


class BlogCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Страница создания новой блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ И ПРАВ - только контент-менеджеры могут создавать статьи.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']
    success_url = reverse_lazy('blog:list')

    # Настройки для LoginRequiredMixin
    login_url = '/users/login/'
    permission_denied_message = 'Для создания статей необходимы права контент-менеджера'

    def test_func(self):
        """Проверяем, является ли пользователь контент-менеджером."""
        return (self.request.user.is_authenticated and
                self.request.user.groups.filter(name='Контент-менеджер').exists())

    def handle_no_permission(self):
        """Обрабатываем отсутствие прав."""
        messages.error(
            self.request,
            'Для создания статей в блоге необходимы права контент-менеджера. '
            'Обратитесь к администратору для получения доступа.'
        )
        return super().handle_no_permission()

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        """
        messages.success(
            self.request,
            f'Статья "{form.instance.title}" успешно '
            f'{"опубликована" if form.instance.is_published else "сохранена как черновик"}!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание новой статьи'
        context['form_action'] = 'create'
        context['submit_text'] = 'Создать статью'
        return context


class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Страница редактирования существующей блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ И ПРАВ - только контент-менеджеры могут редактировать статьи.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем права контент-менеджера."""
        return (self.request.user.is_authenticated and
                self.request.user.groups.filter(name='Контент-менеджер').exists())

    def handle_no_permission(self):
        """Обрабатываем отсутствие прав."""
        messages.error(
            self.request,
            'Для редактирования статей в блоге необходимы права контент-менеджера.'
        )
        return super().handle_no_permission()

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного редактирования.
        """
        messages.success(self.request, 'Статья успешно обновлена!')
        return reverse_lazy('blog:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Добавляем информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование: {self.object.title}'
        context['form_action'] = 'update'
        context['submit_text'] = 'Сохранить изменения'
        return context


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Страница подтверждения удаления блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ И ПРАВ - только контент-менеджеры могут удалять статьи.
    """
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:list')
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем права контент-менеджера."""
        return (self.request.user.is_authenticated and
                self.request.user.groups.filter(name='Контент-менеджер').exists())

    def handle_no_permission(self):
        """Обрабатываем отсутствие прав."""
        messages.error(
            self.request,
            'Для удаления статей в блоге необходимы права контент-менеджера.'
        )
        return super().handle_no_permission()

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение об успешном удалении."""
        post_title = self.get_object().title
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Статья "{post_title}" успешно удалена!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление статьи: {self.object.title}'
        return context


"""
ОБЪЯСНЕНИЕ СИСТЕМЫ ПРАВ ДЛЯ БЛОГА:

1. ОБЩЕДОСТУПНЫЕ страницы:
   - BlogListView - просмотр опубликованных статей
   - BlogDetailView - чтение опубликованных статей

   Обычные пользователи видят только опубликованные статьи.

2. ЗАЩИЩЕННЫЕ страницы (для контент-менеджеров):
   - BlogCreateView - создание новых статей
   - BlogUpdateView - редактирование статей  
   - BlogDeleteView - удаление статей

   Только пользователи из группы "Контент-менеджер" могут управлять блогом.

3. Особенности прав доступа:
   - UserPassesTestMixin проверяет принадлежность к группе "Контент-менеджер"
   - Контент-менеджеры видят ВСЕ статьи (включая черновики)
   - Обычные пользователи видят только опубликованные статьи
   - При отсутствии прав показывается понятное сообщение об ошибке

4. Безопасность:
   - Модераторы продуктов НЕ могут управлять блогом
   - Контент-менеджеры НЕ могут модерировать товары
   - Четкое разделение ответственности между группами

Это обеспечивает надежную систему контроля доступа к разным разделам сайта.
"""