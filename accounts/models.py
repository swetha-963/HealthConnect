from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        ADMIN = "admin", "Administrator"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin_user(self) -> bool:
        return self.is_superuser or self.is_staff or self.role == self.Role.ADMIN

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username

    def __str__(self) -> str:
        return f"{self.display_name} ({self.get_role_display()})"
