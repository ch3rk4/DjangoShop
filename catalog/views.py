from django.shortcuts import render
from django.contrib import messages


def home(request):
    """
    Контроллер для отображения главной страницы.

    На данном этапе просто рендерит шаблон без данных из БД,
    так как модели будут добавлены в ДЗ2.
    """
    return render(request, 'catalog/home.html')


def contacts(request):
    """
    Контроллер для отображения страницы контактов.

    Включает обработку формы обратной связи (дополнительное задание).
    """
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Простая валидация
        if name and email and message:
            # В реальном проекте здесь была бы отправка email или сохранение в БД
            # Пока просто показываем сообщение об успехе
            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение успешно отправлено. '
                'Мы свяжемся с вами в ближайшее время.'
            )
        else:
            messages.error(request, 'Пожалуйста, заполните все поля формы.')

    return render(request, 'catalog/contacts.html')