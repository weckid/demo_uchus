from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cabinet/', views.cabinet_view, name='cabinet'),
    path('application/new/', views.application_create_view, name='application_create'),
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path(
        'admin-panel/application/<int:pk>/status/',
        views.admin_update_status_view,
        name='admin_update_status',
    ),
]
