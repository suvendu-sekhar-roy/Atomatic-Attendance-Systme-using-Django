from .import views
from django.urls import path
urlpatterns = [
    path('login', views.admin_login, name ='admin_login'),
    path('dashboard', views.admin_home, name ='admin_home'),
    path('all_employees', views.all_employees, name ='all_employees'),
    path('camera', views.camera, name ='camera'),
    path('all_attendance', views.all_attendance, name ='all_attendance'),
    path('update_employee/<employee_id>', views.update_employee, name ='update_employee'),
    path('delete_employee/<employee_id>', views.delete_employee, name ='delete_employee'),
    path('download_attendance_report', views.download_attendance_report, name ='download_attendance_report'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
]

# path('register', views.admin_register, name ='employee_register'),