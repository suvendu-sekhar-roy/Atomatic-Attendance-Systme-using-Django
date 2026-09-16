from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone

import cv2
import numpy as np

from .models import Attendance
from .face_utils import recognize_faces
from django.views.decorators.csrf import csrf_exempt

def process_checkin(employee):
    today = timezone.localdate()
    attendance, _ = (
        Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=today
        )
    )
    if attendance.check_in_time is None:
        attendance.check_in_time = (timezone.now())
        attendance.save()
        return "Checked In"
    return "Already Checked In"


def process_checkout(employee):
    today = timezone.localdate()
    attendance = (
        Attendance.objects.filter(
            employee=employee,
            attendance_date=today
        ).first()
    )

    if attendance is None:
        return "No Check-In Found"

    attendance.check_out_time = (timezone.now())

    if attendance.check_in_time:
        attendance.active_hours = (attendance.check_out_time - attendance.check_in_time)

    attendance.save()
    return "Checked Out"



@csrf_exempt
def detect_faces(request):
    if request.method != "POST":
        return JsonResponse({ "faces":[] })

    image = request.FILES.get( "image" )
    mode = request.POST.get( "mode" )

    file_bytes = np.asarray( bytearray(image.read()), dtype=np.uint8 )
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    matches = recognize_faces(frame)
    response_faces = []

    for match in matches:
        bbox = match["bbox"]

        # UNKNOWN FACE

        if not match["recognized"]:
            response_faces.append(
                {
                    "bbox": bbox,
                    "recognized": False,
                    "label": "Unknown"
                }
            )
            continue
        employee = (match["employee"])

        # CHECK-IN MODE

        if mode == "checkin":
            status = process_checkin(employee)

        # CHECK-OUT MODE

        elif mode == "checkout":
            status = process_checkout(employee)

        response_faces.append(
            {
                "bbox": bbox,
                "recognized": True,
                "label": f"{employee.fullname} - {status}"
            }
        )
    return JsonResponse({"faces":response_faces })