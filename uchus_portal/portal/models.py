from django.contrib.auth.models import User
from django.db import models


# доп данные пользователя (фио телефон)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')

    def __str__(self):
        return self.full_name


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('qualification', 'Повышение квалификации'),
        ('retraining', 'Переподготовка'),
        ('safety', 'Охрана труда'),
    ]

    name = models.CharField('Название курса', max_length=255)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# заявка на курс
class Application(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'Идёт обучение'),
        (STATUS_COMPLETED, 'Обучение завершено'),
    ]

    PAYMENT_CHOICES = [
        ('card', 'Предоплата по QR-коду'),
        ('transfer', 'Оплата картой МИР'),
        ('cash', 'Постоплата в офисе организации'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='applications')
    start_date = models.DateField('Дата начала обучения')
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.course.name}'

    @property
    def can_leave_review(self):
        # отзыв только когда админ сменил статус
        return self.status != self.STATUS_NEW and not hasattr(self, 'review')


class Review(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='review',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField('Отзыв')
    rating = models.PositiveSmallIntegerField('Оценка', default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отзыв от {self.user.username}'
