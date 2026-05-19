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



