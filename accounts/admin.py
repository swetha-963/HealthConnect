from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HealthConnectUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (
            "HealthConnect profile",
            {
                "fields": (
                    "role",
                    "phone",
                    "address",
                    "city",
                    "date_of_birth",
                    "profile_image",
                )
            },
        ),
    )
