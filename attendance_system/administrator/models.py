from django.db import models

# Create your models here.
class Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        unique_together = (
            "admin_name",
            "admin_email",
            "password"
        )