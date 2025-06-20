from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
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
        Фильтруем только опубликованные статьи.

        Неопубликованные статьи (черновики) не показываем обычным посетителям.
        """
        return BlogPost.objects.filter(is_published=True).order_by('-created_date')

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Блог'
        context['total_posts'] = self.get_queryset().count()

        # Проверяем права пользователя
        if self.request.user.is_authenticated:
            context['can_create_post'] = (
                    self.request.user.groups.filter(name='Контент-менеджер').exists() or
                    self.request.user.is_superuser
            )
        else:
            context['can_create_post'] = False

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
        Показываем только опубликованные статьи.

        Это предотвращает доступ к черновикам через прямую ссылку.
        """
        return BlogPost.objects.filter(is_published=True)

    def get_object(self, queryset=None):
        """
        Переопределяем получение объекта для увеличения счетчика просмотров.
        """
        # Сначала получаем объект стандартным способом
        obj = super().get_object(queryset)

        # Увеличиваем счетчик просмотров
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

    def get_context_data(self, **kwargs):
        """Добавляем права пользователя в контекст."""
        context = super().get_context_data(**kwargs)

        # Проверяем права на редактирование и удаление
        if self.request.user.is_authenticated:
            context['can_edit_post'] = (
                    self.request.user.groups.filter(name='Контент-менеджер').exists() or
                    self.request.user.is_superuser
            )
            context['can_delete_post'] = context['can_edit_post']
        else:
            context['can_edit_post'] = False
            context['can_delete_post'] = False

        return context


class ContentManagerTestMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав контент-менеджера.
    """

    def test_func(self):
        """Проверяем, является ли пользователь контент-менеджером."""
        return (
                self.request.user.groups.filter(name='Контент-менеджер').exists() or
                self.request.user.is_superuser
        )

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(
            self.request,
            'У вас нет прав для управления блогом. '
            'Только контент-менеджеры могут выполнять это действие.'
        )
        return redirect('blog:blog_list')


class BlogCreateView(LoginRequiredMixin, ContentManagerTestMixin, CreateView):
    """
    Страница создания новой блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ и прав контент-менеджера.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']
    success_url = reverse_lazy('blog:list')

    # Настройки для LoginRequiredMixin
    login_url = '/users/login/'
    permission_denied_message = 'Для создания статей необходимо войти в систему'

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        """
        messages.success(
            self.request,
            f'Статья "{form.instance.title}" успешно {'опубликована' if form.instance.is_published else 'сохранена как черновик'}!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание новой статьи'
        context['form_action'] = 'create'
        context['submit_text'] = 'Создать статью'
        return context


class BlogUpdateView(LoginRequiredMixin, ContentManagerTestMixin, UpdateView):
    """
    Страница редактирования существующей блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ и прав контент-менеджера.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']
    login_url = '/users/login/'

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


class BlogDeleteView(LoginRequiredMixin, ContentManagerTestMixin, DeleteView):
    """
    Страница подтверждения удаления блоговой записи.

    ТРЕБУЕТ АВТОРИЗАЦИИ и прав контент-менеджера.
    """
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:list')
    login_url = '/users/login/'

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
ОБЪЯСНЕНИЕ БЕЗОПАСНОСТИ БЛОГА С ГРУППАМИ:

1. ОБЩЕДОСТУПНЫЕ страницы:
   - BlogListView - список опубликованных статей
   - BlogDetailView - чтение опубликованных статей

   Работают как публичная библиотека - читать могут все.

2. ЗАЩИЩЕННЫЕ страницы (с ContentManagerTestMixin):
   - BlogCreateView - создание новых статей
   - BlogUpdateView - редактирование статей
   - BlogDeleteView - удаление статей

   Доступны только контент-менеджерам и администраторам.

3. Группа "Контент-менеджер":
   - Может создавать новые статьи
   - Может редактировать любые статьи
   - Может удалять любые статьи
   - Может управлять публикацией статей

4. Обычные пользователи и модераторы продуктов:
   - НЕ могут создавать статьи
   - НЕ могут редактировать статьи
   - НЕ могут удалять статьи
   - Могут только читать опубликованные статьи

Такая архитектура обеспечивает четкое разделение прав между 
управлением продуктами и управлением контентом блога.
"""