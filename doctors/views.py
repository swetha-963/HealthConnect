from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.emails import send_appointment_booked_email

from .forms import AppointmentForm
from .models import Appointment, Doctor, Specialization


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related("specialization")
    query = request.GET.get("q", "").strip()
    specialization = request.GET.get("specialization", "").strip()

    if query:
        doctors = doctors.filter(
            Q(full_name__icontains=query)
            | Q(qualification__icontains=query)
            | Q(specialization__name__icontains=query)
        )
    if specialization:
        doctors = doctors.filter(specialization__slug=specialization)

    paginator = Paginator(doctors, 9)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "doctors/list.html",
        {
            "page_obj": page,
            "doctors": page.object_list,
            "specializations": Specialization.objects.all(),
            "query": query,
            "active_specialization": specialization,
        },
    )


def doctor_detail(request, slug):
    doctor = get_object_or_404(
        Doctor.objects.select_related("specialization"), slug=slug, is_active=True
    )
    schedules = [s for s in doctor.available_schedules if s.is_bookable]
    return render(
        request,
        "doctors/detail.html",
        {"doctor": doctor, "schedules": schedules, "form": AppointmentForm(doctor=doctor)},
    )


@login_required
def book_appointment(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug, is_active=True)
    form = AppointmentForm(request.POST or None, doctor=doctor)

    if request.method == "POST":
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            appointment.save()
            send_appointment_booked_email(appointment)
            messages.success(
                request,
                f"Appointment {appointment.reference} requested. You will be notified once it is confirmed.",
            )
            return redirect("doctors:my_appointments")
        messages.error(request, "Please correct the errors below.")

    schedules = [s for s in doctor.available_schedules if s.is_bookable]
    return render(
        request,
        "doctors/detail.html",
        {"doctor": doctor, "schedules": schedules, "form": form},
    )


@login_required
def my_appointments(request):
    appointments = (
        Appointment.objects.filter(patient=request.user)
        .select_related("doctor", "schedule")
    )
    return render(
        request, "doctors/my_appointments.html", {"appointments": appointments}
    )


@login_required
def cancel_appointment(request, reference):
    appointment = get_object_or_404(
        Appointment, reference=reference, patient=request.user
    )
    if request.method != "POST":
        return redirect("doctors:my_appointments")
    if appointment.status in {Appointment.Status.COMPLETED, Appointment.Status.CANCELLED}:
        messages.warning(request, "This appointment can no longer be cancelled.")
    else:
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        messages.info(request, f"Appointment {appointment.reference} cancelled.")
    return redirect("doctors:my_appointments")
