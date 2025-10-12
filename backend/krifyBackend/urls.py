# faceapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("projects", views.project_list, name="projects"),
    path("top-projects", views.top_projects, name="top-projects"),
    path("employ-login", views.employ_login, name="employ-login"),
    path("intern-login", views.intern_login, name="intern-login"),
    path("Forget-password", views.Forget_password, name="forget"),
    path("Verify-otp", views.verify_OTP, name="verify-otp"),
    path("Reset-password", views.Reset_Password, name="Reset-password"),
    path("profile-card", views.profile_card, name="profile-card"),
]
