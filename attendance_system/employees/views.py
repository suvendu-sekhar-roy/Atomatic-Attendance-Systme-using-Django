# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import date
#import pandas as pd
from django.http import HttpResponse
from .models import Employee
import cv2
from insightface.app import FaceAnalysis
from attendance.models import Attendance

# Load InsightFace model once
face_app = FaceAnalysis(
    providers=['CPUExecutionProvider']
)
face_app.prepare(
  #  ctx_id=0,
    det_size=(640, 640)
)

def employee_home(request):
    employee_id = request.session.get('employee_id')
    employee = Employee.objects.get(employee_id = employee_id)
    records = Attendance.objects.filter(
        employee__employee_id=employee_id
    )
    # Current month attendance count
    today = timezone.localdate()
    present_count = Attendance.objects.filter(
        employee=employee,
        attendance_date__year=today.year,
        attendance_date__month=today.month
    ).count()
    absent_count = 30 - present_count

    attendance_rate = round((present_count / 30) * 100, 2)

    return render(request,'employees/employee_page.html',
                {"employee": employee,
                         "records": records,
                         "present_count": present_count,
                        "absent_count": absent_count,
                        "attendance_rate": attendance_rate,
                        "today": date.today()
                        })


def employee_registration(request):

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        employee_id = request.POST.get("employee_id")
        department = request.POST.get("department")
        designation = request.POST.get("designation")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        profile_picture = request.FILES.get("profile_picture")

        # -----------------------------
        # Employee ID already exists
        # -----------------------------
        if Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already exists.")
            return redirect("/employees/register")

        # -----------------------------
        # Email already exists
        # -----------------------------
        if Employee.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("/employees/register")

        # -----------------------------
        # Password Match
        # -----------------------------
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("/employees/register")

        # -----------------------------
        # Django Password Validation
        # -----------------------------
        try:
            validate_password(password)

        except ValidationError as e:

            for error in e.messages:
                messages.error(request, error)

            return redirect("/employees/register")

        # -----------------------------
        # Save Employee
        # -----------------------------
        employee = Employee.objects.create(
            fullname=fullname,
            employee_id=employee_id,
            department=department,
            designation=designation,
            phone=phone,
            email=email,
            password=make_password(password),
            profile_picture=profile_picture
        )

        success = train_new_face(employee)

        if not success:
            employee.delete()

            messages.error(
                request,
                "Face could not be detected. Please upload a proper passport-size photo."
            )

            return redirect("/employees/register")

        messages.success(request, "Registered Successfully.")
        print(employee.profile_picture)
        print(employee.profile_picture.path)
        return redirect("/employees/login")

    return render(request, "employees/employee_registration.html")

def employee_login(request):

    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        try:
            employee = Employee.objects.get(employee_id=employee_id)

            print("Employee Found")

            result = check_password(password, employee.password)
            print("Password Match:", result)
            if result:
                request.session["employee_id"] = employee.employee_id
                return redirect("/employees/dashboard")

            messages.error(request, "Invalid Employee ID or Password")
            print("Invalid Employee ID or Password")

        except Employee.DoesNotExist:
            print("Employee not found")
            messages.error(request, "Invalid Employee ID or Password")

        return redirect("/employees/login")

    return render(request, "employees/employee_login.html")

def train_new_face(employee):

    # Get uploaded image path
    image_path = employee.profile_picture.path

    # Read image
    img = cv2.imread(image_path)

    if img is None:
        print("Cannot read image")
        return False

    # Detect faces
    faces = face_app.get(img)

    # No face found
    if len(faces) == 0:
        print("No face detected")
        return False

    # More than one face found
    if len(faces) > 1:
        print("Multiple faces detected")
        return False

    # Get 512-dimensional embedding
    embedding = faces[0].embedding

    # Convert numpy array to list
    embedding_list = embedding.tolist()

    # Save directly in PostgreSQL
    employee.face_encoding = embedding_list

    employee.save()
    print(f"{employee.employee_id} encoded successfully")
    return True

def employee_profile(request):
        employee_pk = request.session.get("employee_id")

        if not employee_pk:
            return redirect("/employees/login")

        try:
            employee = Employee.objects.get(employee_id=employee_pk)

        except Employee.DoesNotExist:
            return redirect("/employees/login")

        return render(
            request,
            "employees/employee_profile.html",
            {
                "employee": employee
            }
        )

def edit_profile(request):
    employee_id = request.session.get("employee_id")
    if not employee_id:
        messages.error(request,"Please login first.")
        return redirect("/employees/login")

    try:
        employee = Employee.objects.get(employee_id=employee_id)

    except Employee.DoesNotExist:
        messages.error(request,"Employee not found.")
        return redirect("/employees/login")

    if request.method == "POST":

        # Update Basic Details
        employee.fullname = request.POST.get("fullname")
        employee.email = request.POST.get("email")
        employee.phone = request.POST.get("phone")
        employee.department = request.POST.get("department")
        employee.designation = request.POST.get("designation")

        # Optional Password Change

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Run password validation ONLY if current password entered

        if current_password:
            if not check_password(current_password,employee.password):
                messages.error(request,"Current password is incorrect.")
                return redirect("/employees/profile")

            if not new_password:
                messages.error(request,"Please enter a new password.")
                return redirect("/employees/profile")

            if new_password != confirm_password:
                messages.error(request,"New password and confirm password do not match.")

                return redirect("/employees/profile")

            try:
                validate_password(new_password)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request,error)
                return redirect("/employees/profile")

            employee.password = make_password(new_password)
            print(f"Password updated for "f"{employee.employee_id}")

        # Save all changes

        employee.save()
        messages.success(request,"Profile updated successfully.")

        return redirect("/employees/profile")

    return render(
        request,
        "employees/employee_profile.html",
        {
            "employee": employee
        }
    )

def change_photo(request):

    employee_id = request.session.get("employee_id")

    if not employee_id:
        return redirect("/employees/login")

    try:
        employee = Employee.objects.get(id=employee_id)

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect("/employees/login")

    if request.method == "POST":

        new_photo = request.FILES.get("profile_picture")
        print("POST Request Received")
        print(new_photo)


        if not new_photo:

            messages.error(
                request,
                "Please select a photo."
            )

            return redirect("/employees/profile")

        employee.profile_picture = new_photo
        employee.save()

        success = train_new_face(employee)

        if not success:

            messages.error(request,"Face could not be detected in uploaded image.")
            return redirect("/employees/profile")

        messages.success(request,"Photo updated successfully."
        )

        return redirect("/employees/profile")

    return redirect("/employees/profile")

def employee_logout(request):

    request.session.flush()
    # auth.logout(request)
    messages.success(request,"Logged out successfully.")

    return redirect("/")

def download_attendance(request):

    employee_id = request.session.get(
        "employee_id"
    )

    employee = Employee.objects.get(
        employee_id=employee_id
    )

    records = Attendance.objects.filter(
        employee=employee
    ).order_by("-attendance_date")

    data = []

    for record in records:

        data.append({

            "Date": record.attendance_date,

            "Check In":
            record.check_in_time.strftime(
                "%I:%M:%S %p"
            )
            if record.check_in_time else "",

            "Check Out":
            record.check_out_time.strftime(
                "%I:%M:%S %p"
            )
            if record.check_out_time else "",

            "Active Hour":
            str(record.active_hours)
            if record.active_hours else ""

        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="Attendance_{employee.employee_id}.xlsx"'
    )

    with pd.ExcelWriter(
        response,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Attendance",
            index=False
        )

    return response