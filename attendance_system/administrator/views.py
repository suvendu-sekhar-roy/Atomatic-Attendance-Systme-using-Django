from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Admin
from datetime import date
from django.http import HttpResponse

from attendance.models import Attendance
from employees.models import Employee
from django.shortcuts import get_object_or_404
#import pandas as pd
# Create your views here.

employees = Employee.objects.all()
records = Attendance.objects.select_related("employee")

employee_count = employees.count()
#today = timezone.localdate()
today = date.today()

present_count = Attendance.objects.filter(
    attendance_date=today,
    check_in_time__isnull=False
).count()
absent_count = employee_count-present_count

@login_required(login_url='admin_login')
def admin_home(request):
    attendance_records = []

    for employee in employees:
        attendance = Attendance.objects.filter(
            employee=employee,
            attendance_date=today
        ).first()

        if attendance:
            attendance_records.append({
                "employee": employee,
                "date": attendance.attendance_date,
                "check_in": attendance.check_in_time,
                "check_out": attendance.check_out_time,
                "duration": attendance.active_hours,
                "status": "Present"
            })
        else:
            attendance_records.append({
                "employee": employee,
                "date": today,
                "check_in": None,
                "check_out": None,
                "duration": None,
                "status": "Absent"
            })

    return render(
        request,
        "administrator/admin_page.html",
        {
            "employees": employees,
            "records": records,
            "employee_count": employee_count,
            "present_count": present_count,
            "absent_count": absent_count,
            "today": date.today(),
            "attendance_records": attendance_records
        }
    )


def admin_login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user and user.is_superuser:
                login(request, user)
                request.session["username"] = user.username

                return redirect('/admin/dashboard')

            messages.info(request, 'Invalid admin id or password')
            return redirect('/admin/login')

        return render(request, 'administrator/admin_login.html')

    except Exception as e:
        print("Error:", e)
        return redirect('/admin/login')

@login_required(login_url='admin_login')
def update_employee(request,employee_id):
    # queryset = Employee.objects.get(employee_id=employee_id)
    # employee_id = request.session.get("employee_id")
    try:
        employee = Employee.objects.get(employee_id=employee_id)

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")

        return redirect("/admin/all_employees")

    if request.method == "POST":

        # -----------------------------------
        # Update Basic Details
        # -----------------------------------

        employee.fullname = request.POST.get("fullname")
        employee.email = request.POST.get("email")
        employee.phone = request.POST.get("phone")
        employee.department = request.POST.get("department")
        employee.designation = request.POST.get("designation")

        # -----------------------------------
        # Save all changes
        # -----------------------------------

        employee.save()
        messages.success(request,"Profile updated successfully.")

        return redirect("/admin/all_employees")

    return render(
        request,
        "administrator/update_employee.html",
        {
            "employee": employee
        }
    )

@login_required(login_url='admin_login')
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.delete()
    return redirect('/admin/all-employees')


@login_required(login_url='admin_login')
def all_employees(request):
    # employees = Employee.objects.all()
    return render(
        request,
        "administrator/all_employees.html",{"employees": employees })

@login_required(login_url='admin_login')
def camera (request):
    return render(request,"administrator/camera.html")


@login_required(login_url='admin_login')
def all_attendance(request):

    total_days = Attendance.objects.values('attendance_date').distinct().count()

    #employees = Employee.objects.all()

    employee_records = []

    for employee in employees:
        days_present = Attendance.objects.filter(
            employee=employee,
        ).count()
        attendance_rate = 0
        if total_days > 0:
            attendance_rate = round((days_present / total_days) * 100,2)

        employee_records.append({
            'employee_name': employee.fullname,
            'days_present': days_present,
            'attendance_rate': attendance_rate
        })

    context = {
        'employee_records': employee_records,
        "employees": employees,
        "employee_count": employee_count,
        "present_count": present_count,
        "absent_count": absent_count,
        "today": date.today(),

    }

    return render(request, "administrator/all_attendance.html",context)

@login_required(login_url='admin_login')
def download_attendance_report(request):

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    response["Content-Disposition"] = (
        'attachment; filename="All_Attendance_Report.xlsx"'
    )

    with pd.ExcelWriter(response,engine="openpyxl") as writer:

        # All attendance dates
        dates = (Attendance.objects
            .values_list("attendance_date",flat=True)
            .distinct()
            .order_by("-attendance_date")
        )

        for report_date in dates:
            data = []
            all_employees = Employee.objects.all()
            for employee in all_employees:
                attendance = Attendance.objects.filter(
                    employee=employee,
                    attendance_date=report_date
                ).first()

                if attendance:
                    check_in = (
                        attendance.check_in_time.strftime(
                            "%I:%M:%S %p"
                        )
                        if attendance.check_in_time
                        else ""
                    )

                    check_out = (
                        attendance.check_out_time.strftime(
                            "%I:%M:%S %p"
                        )
                        if attendance.check_out_time
                        else ""
                    )

                    active_hours = (
                        str(attendance.active_hours)
                        if attendance.active_hours
                        else ""
                    )
                    status = "Present"

                else:
                    check_in = ""
                    check_out = ""
                    active_hours = ""
                    status = "Absent"

                data.append({
                    "Employee ID": employee.employee_id,
                    "Employee Name": employee.fullname,
                    "Check In": check_in,
                    "Check Out": check_out,
                    "Active Hours":  active_hours,
                    "Status": status
                })

            df = pd.DataFrame(data)
            sheet_name = (report_date.strftime("%d-%b-%Y"))

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )
    return response

def admin_logout(request):
    logout(request)
    # auth.logout(request)
    messages.success(request,"Logged out successfully.")

    return redirect("/")

# def admin_register(request):
# 
#     if request.method == "POST":
# 
#         username = request.POST["admin_name"]
#         email = request.POST["admin_email"]
#         password = request.POST["password"]
# 
#         Admin.objects.create(
#             admin_name=username,
#             admin_email=email,
#             password=make_password(password)
#         )
# 
#         messages.success(
#             request,
#             "Admin registered successfully."
#         )
# 
#         return redirect("admin_login")
# 
#     return render(
#         request,
#         "admins/register.html"
#     )
