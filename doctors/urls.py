from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="list"),
    path("appointments/", views.my_appointments, name="my_appointments"),
    path("appointments/<str:reference>/cancel/", views.cancel_appointment, name="cancel_appointment"),
    path("<slug:slug>/", views.doctor_detail, name="detail"),
    path("<slug:slug>/book/", views.book_appointment, name="book"),
]
