from django.db import models
#from employees.models import Employee

class Attendance(models.Model):

    employee = models.ForeignKey('employees.Employee',on_delete=models.CASCADE)

    attendance_date = models.DateField()

    check_in_time = models.DateTimeField(null=True,blank=True)

    check_out_time = models.DateTimeField(null=True,blank=True)

    active_hours = models.DurationField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = (
            'employee',
            'attendance_date'
        )

    def __str__(self):
        return (
            f"{self.employee.employee_id}"
        )