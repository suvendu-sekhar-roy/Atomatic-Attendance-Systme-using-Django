from django.urls import path
from . import views


#yet to configure correctly
urlpatterns = [


    path("checkin/",views.process_checkin, name="check_in"),

    path("checkout/",views.process_checkout,name="check_out"),

    #path("report/",views.attendance_report,name="attendance_report"),

    path("detect_faces/",views.detect_faces, name="detect_faces"),

]
