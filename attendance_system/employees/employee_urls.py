from django.urls import path
from .import views

urlpatterns = [
    path('login', views.employee_login, name ='employee_login'),
    path('register', views.employee_registration, name ='employee_registration'),
    #path('employee_attendance', views.employee_attendance, name ='employee_attendance'),
    path('dashboard', views.employee_home, name ='employee_home'),
    path('profile', views.employee_profile, name ='employee_profile'),
    path('edit_profile', views.edit_profile, name ='edit_profile'),
    path('change_photo', views.change_photo, name ='change_photo'),
    path('employee_logout', views.employee_logout, name ='employee_logout'),
    path("download-attendance", views.download_attendance, name="download_attendance")
]