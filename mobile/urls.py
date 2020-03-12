from django.urls import path, re_path

from mobile import views


urlpatterns = [
    path('', views.IndexView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logoff', views.LogoffView.as_view()),
]