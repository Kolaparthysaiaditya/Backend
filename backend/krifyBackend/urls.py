# faceapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("projects", views.project_list, name="projects"),
    path("projectInfo", views.projectInfo, name="projectInfo"),
    path('projects/add/', views.add_project, name='add_project'),
    path('projectInfo/update-status/<int:pk>/', views.update_status_deadline, name="projectdataupdate"),

    path("top-projects", views.top_projects, name="top-projects"),
    path("employ-login", views.employ_login, name="employ-login"),
    path("intern-login", views.intern_login, name="intern-login"),

    path("Forget-password", views.Forget_password, name="forget"),
    path("Verify-otp", views.verify_OTP, name="verify-otp"),
    path("Reset-password", views.Reset_Password, name="Reset-password"),

    path("profile-card", views.profile_card, name="profile-card"),
    path("previce-Projects", views.previous_projects_by_ids, name="previce-projects"),
    path("current-project/", views.current_project, name="current-project"),

    path("get-interns", views.get_interns, name="get-interns"),
    path("delete-intern/<str:iid>/", views.delete_intern, name="delete-intern"),
    path("add-intern/", views.add_intern, name="add-intern"),

    path("get-employees", views.get_employees, name="get-employees"),
    path('mark_attendance/', views.mark_attendance, name="mark-attendance"),
    path('mark_checkout/', views.mark_checkout, name="markCheckout"),
    path('attendance/all/employees/', views.get_all_employees_attendance, name="all_employess_attandeance"),
    path('attendance/all/interns/', views.get_all_intern_attadence, name="all_interns_attendance"),

    path('attendance/employee/', views.get_employee_attendance, name="employee_attandece"),
    path('attendance/interns/', views.get_intern_attendance, name="intern_attendance"),

]
