from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('content/', views.content, name='content'),
    path('accounts/login/', auth_views.LoginView.as_view()),
]
