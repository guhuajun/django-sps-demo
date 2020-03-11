from django.urls import path, re_path

from mobile import views


urlpatterns = [
    path('', views.IndexView.as_view()),
]