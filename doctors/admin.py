from django.contrib import admin

from .models import Appointment, Doctor, DoctorSchedule, Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialization", "experience_years", "consultation_fee", "is_active")
    list_filter = ("specialization", "is_active", "gender")
    search_fields = ("full_name", "qualification", "email")


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "start_time", "end_time", "slot_limit", "is_available")
    list_filter = ("is_available", "date", "doctor")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("reference", "patient_name", "doctor", "schedule", "status", "confirmed")
    list_filter = ("status", "confirmed", "doctor")
    search_fields = ("reference", "patient_name", "patient_email")
