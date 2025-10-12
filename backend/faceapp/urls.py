# faceapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_page, name="register_page"),
    path("api/register_capture/", views.register_capture, name="register_capture"),
    path("api/login_capture/", views.login_capture, name="login_capture"),
    path("hello/",views.hello, name="hello")
]
