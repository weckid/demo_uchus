from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AdminStatusForm, ApplicationForm, LoginForm, RegistrationForm, ReviewForm
from .models import Application, Review

# данные админа из задания
ADMIN_LOGIN = 'Admin26'
ADMIN_PASSWORD = 'Demo20'
ADMIN_SESSION_KEY = 'portal_admin'


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get(ADMIN_SESSION_KEY):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)

    return wrapper


def home(request):
    if request.session.get(ADMIN_SESSION_KEY):
        return redirect('admin_panel')
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


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if username == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            request.session[ADMIN_SESSION_KEY] = True  # запоминаем что админ вошел
            messages.success(request, 'Добро пожаловать в панель администратора.')
            return redirect('admin_panel')
        messages.error(request, 'Неверные учётные данные администратора.')

    return render(request, 'admin_login.html')


def admin_logout_view(request):
    request.session.pop(ADMIN_SESSION_KEY, None)
    messages.info(request, 'Выход из панели администратора.')
    return redirect('admin_login')


@admin_required
def admin_panel_view(request):
    queryset = Application.objects.select_related('user', 'user__profile', 'course', 'review')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-created_at')

    allowed_sorts = {
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'status': 'status',
        '-status': '-status',
        'user': 'user__username',
        '-user': '-user__username',
    }
    order_by = allowed_sorts.get(sort, '-created_at')

    # фильтры для админки
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(
            Q(user__username__icontains=search)
            | Q(user__profile__full_name__icontains=search)
            | Q(course__name__icontains=search)
        )

    queryset = queryset.order_by(order_by)

    paginator = Paginator(queryset, 5)  # по 5 заявок на странице
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_panel.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'sort': sort,
        'status_choices': Application.STATUS_CHOICES,
    })


@admin_required
@require_POST
def admin_update_status_view(request, pk):
    application = get_object_or_404(Application, pk=pk)
    form = AdminStatusForm(request.POST)
    if form.is_valid():
        application.status = form.cleaned_data['status']
        application.save()
        messages.success(request, f'Статус заявки #{pk} обновлён.')
    else:
        messages.error(request, 'Не удалось обновить статус.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel'))
