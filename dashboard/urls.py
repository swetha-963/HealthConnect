from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    # Doctors
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/add/", views.doctor_add, name="doctor_add"),
    path("doctors/<int:pk>/edit/", views.doctor_edit, name="doctor_edit"),
    path("doctors/<int:pk>/image/", views.doctor_image, name="doctor_image"),
    path("doctors/<int:pk>/delete/", views.doctor_delete, name="doctor_delete"),
    path("specializations/add/", views.specialization_add, name="specialization_add"),
    # Schedules
    path("schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/add/", views.schedule_add, name="schedule_add"),
    path("schedules/<int:pk>/edit/", views.schedule_edit, name="schedule_edit"),
    path("schedules/<int:pk>/toggle/", views.schedule_toggle, name="schedule_toggle"),
    path("schedules/<int:pk>/delete/", views.schedule_delete, name="schedule_delete"),
    # Appointments
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/<int:pk>/confirm/", views.appointment_confirm, name="appointment_confirm"),
    path("appointments/<int:pk>/status/", views.appointment_status, name="appointment_status"),
    # Medicines
    path("medicines/", views.medicine_list, name="medicine_list"),
    path("medicines/add/", views.medicine_add, name="medicine_add"),
    path("medicines/<int:pk>/edit/", views.medicine_edit, name="medicine_edit"),
    path("medicines/<int:pk>/delete/", views.medicine_delete, name="medicine_delete"),
    path("categories/add/", views.category_add, name="category_add"),
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<str:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<str:order_id>/status/", views.order_status_update, name="order_status_update"),
]
