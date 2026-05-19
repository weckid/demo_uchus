import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Application, Course, Review, UserProfile


class RegistrationForm(forms.Form):
    login = forms.CharField(
        label='Логин',
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'До 6 символов'}),
    )
    password = forms.CharField(
        label='Пароль',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Минимум 8 символов'}),
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    full_name = forms.CharField(
        label='ФИО',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    phone = forms.CharField(
        label='Контактный телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7...'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    def clean_login(self):
        login = self.cleaned_data['login'].strip()
        # по тз логин латиница и цифры
        if not re.fullmatch(r'[A-Za-z0-9]+', login):
            raise ValidationError('Логин: только латинские буквы и цифры.')
        if len(login) > 6:
            raise ValidationError('Логин: не более 6 символов.')
        if User.objects.filter(username=login).exists():
            raise ValidationError('Этот логин уже занят.')
        return login

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать не менее 8 символов.')
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')
        return cleaned

    def save(self):
        # создаем user и профиль
        login = self.cleaned_data['login']
        user = User.objects.create_user(
            username=login,
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )
        UserProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email'],
        )
        return user


class LoginForm(forms.Form):
    login = forms.CharField(
        label='Логин',
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['course', 'start_date', 'payment_method']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
            ),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'course': 'Курс',
            'start_date': 'Дата начала обучения',
            'payment_method': 'Способ оплаты',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.Select(
                choices=[(i, str(i)) for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
        }
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка',
        }


class AdminStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Application.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
