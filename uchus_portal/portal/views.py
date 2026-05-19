from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AdminStatusForm, ApplicationForm, LoginForm, RegistrationForm, ReviewForm
from .models import Application, Review



def home(request):

    if request.user.is_authenticated:
        return redirect('cabinet')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet')

    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            return redirect('cabinet')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            # проверка логина и пароля
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('cabinet')
            messages.error(request, 'Неверный логин или пароль. Проверьте данные и попробуйте снова.')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


@login_required
def cabinet_view(request):
    applications = Application.objects.filter(user=request.user).select_related('course', 'review')
    review_forms = {}
    for app in applications:
        if app.can_leave_review:
            review_forms[app.pk] = ReviewForm()

    # отправка отзыва
    if request.method == 'POST' and 'application_id' in request.POST:
        app_id = request.POST.get('application_id')
        application = get_object_or_404(Application, pk=app_id, user=request.user)
        if application.can_leave_review:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.application = application
                review.user = request.user
                review.save()
                messages.success(request, 'Спасибо за отзыв!')
                return redirect('cabinet')
            review_forms[int(app_id)] = form
        else:
            messages.warning(request, 'Отзыв можно оставить только после смены статуса администратором.')

    return render(request, 'cabinet.html', {
        'applications': applications,
        'review_forms': review_forms,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def application_create_view(request):
    form = ApplicationForm()
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Заявка отправлена на согласование администратору.')
            return redirect('cabinet')

    return render(request, 'application_form.html', {'form': form})

