from django.db import models


class Employee(models.Model):
    employee_id = models.CharField(
        max_length=20,
        primary_key=True
    )
    fullname = models.CharField(max_length=100)

    department = models.CharField(max_length=50)

    designation = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=255)


    profile_picture = models.ImageField(
        upload_to='employee_photos/'
    )

    # Stores the 128-dimensional face encoding16
    face_encoding = models.JSONField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.employee_id