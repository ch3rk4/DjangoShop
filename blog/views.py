from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import BlogPost


class BlogListView(ListView):
    """
    Страница со списком всех блоговых записей.
    """
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6  # Показываем по 6 статей на странице

    def get_queryset(self):
        """
        Фильтруем только опубликованные статьи.
        """
        return BlogPost.objects.filter(is_published=True).order_by('-created_date')

    def get_context_data(self, **kwargs):
        """Добавляем дополнительную информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Блог'
        context['total_posts'] = self.get_queryset().count()
        return context


class BlogDetailView(DetailView):
    """
    Страница детального просмотра одной статьи.
    """
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

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


class BlogCreateView(CreateView):
    """
    Страница создания новой блоговой записи.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        """
        Вызывается при успешной валидации формы.
        """
        messages.success(self.request, 'Статья успешно создана!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание новой статьи'
        context['form_action'] = 'create'
        return context


class BlogUpdateView(UpdateView):
    """
    Страница редактирования существующей блоговой записи.
    """
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview_image', 'is_published']

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного редактирования.
        """
        messages.success(self.request, 'Статья успешно обновлена!')
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Добавляем информацию для шаблона."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование: {self.object.title}'
        context['form_action'] = 'update'
        return context


class BlogDeleteView(DeleteView):
    """
    Страница подтверждения удаления блоговой записи.
    """
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение об успешном удалении."""
        messages.success(request, 'Статья успешно удалена!')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление статьи: {self.object.title}'
        return context