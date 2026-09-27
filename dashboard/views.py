from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.emails import send_appointment_confirmed_email, send_order_status_email
from doctors.forms import (
    DoctorForm,
    DoctorImageForm,
    DoctorScheduleForm,
    SpecializationForm,
)
from doctors.models import Appointment, Doctor, DoctorSchedule, Specialization
from pharmacy.forms import CategoryForm, MedicineForm, OrderStatusForm
from pharmacy.models import Category, Medicine, Order

from .decorators import admin_required


@admin_required
def dashboard_home(request):
    today = timezone.localdate()
    orders = Order.objects.all()
    revenue = (
        orders.exclude(status=Order.Status.CANCELLED).aggregate(total=Sum("total"))[
            "total"
        ]
        or 0
    )
    stats = {
        "doctors": Doctor.objects.filter(is_active=True).count(),
        "appointments": Appointment.objects.count(),
        "pending_appointments": Appointment.objects.filter(
            status=Appointment.Status.PENDING
        ).count(),
        "today_appointments": Appointment.objects.filter(schedule__date=today).count(),
        "medicines": Medicine.objects.filter(is_active=True).count(),
        "low_stock": Medicine.objects.filter(is_active=True, stock__lte=10).count(),
        "orders": orders.count(),
        "pending_orders": orders.filter(status=Order.Status.PENDING).count(),
        "revenue": revenue,
    }
    return render(
        request,
        "dashboard/home.html",
        {
            "stats": stats,
            "recent_appointments": Appointment.objects.select_related(
                "doctor", "schedule"
            )[:6],
            "recent_orders": orders[:6],
            "low_stock_medicines": Medicine.objects.filter(
                is_active=True, stock__lte=10
            ).order_by("stock")[:6],
        },
    )


# ---------------------------------------------------------------- doctors


@admin_required
def doctor_list(request):
    doctors = (
        Doctor.objects.select_related("specialization")
        .annotate(
            schedule_count=Count("schedules", distinct=True),
            appointment_count=Count("appointments", distinct=True),
        )
        .order_by("full_name")
    )
    query = request.GET.get("q", "").strip()
    if query:
        doctors = doctors.filter(
            Q(full_name__icontains=query) | Q(specialization__name__icontains=query)
        )
    page = Paginator(doctors, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/doctor_list.html",
        {"page_obj": page, "doctors": page.object_list, "query": query},
    )


@admin_required
def doctor_add(request):
    form = DoctorForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save()
        messages.success(request, f"Doctor {doctor.full_name} added.")
        return redirect("dashboard:doctor_list")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(
        request,
        "dashboard/doctor_form.html",
        {"form": form, "title": "Add doctor", "doctor": None},
    )


@admin_required
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, request.FILES or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Doctor {doctor.full_name} updated.")
        return redirect("dashboard:doctor_list")
    return render(
        request,
        "dashboard/doctor_form.html",
        {"form": form, "title": f"Edit {doctor.full_name}", "doctor": doctor},
    )


@admin_required
def doctor_image(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorImageForm(request.POST or None, request.FILES or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Photo updated for {doctor.full_name}.")
        return redirect("dashboard:doctor_list")
    if request.method == "POST":
        messages.error(request, "Please choose a valid image file (max 5 MB).")
    return render(
        request, "dashboard/doctor_image.html", {"form": form, "doctor": doctor}
    )


@admin_required
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == "POST":
        name = doctor.full_name
        doctor.delete()
        messages.info(request, f"Doctor {name} removed.")
    return redirect("dashboard:doctor_list")


@admin_required
def specialization_add(request):
    form = SpecializationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        specialization = form.save()
        messages.success(request, f"Specialization {specialization.name} added.")
        return redirect("dashboard:doctor_add")
    return render(
        request,
        "dashboard/specialization_form.html",
        {"form": form, "specializations": Specialization.objects.all()},
    )


# --------------------------------------------------------------- schedules


@admin_required
def schedule_list(request):
    schedules = DoctorSchedule.objects.select_related("doctor").all()
    doctor_id = request.GET.get("doctor", "").strip()
    availability = request.GET.get("availability", "").strip()
    if doctor_id:
        schedules = schedules.filter(doctor_id=doctor_id)
    if availability == "available":
        schedules = schedules.filter(is_available=True)
    elif availability == "unavailable":
        schedules = schedules.filter(is_available=False)
    page = Paginator(schedules, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/schedule_list.html",
        {
            "page_obj": page,
            "schedules": page.object_list,
            "doctors": Doctor.objects.filter(is_active=True),
            "doctor_id": doctor_id,
            "availability": availability,
        },
    )


@admin_required
def schedule_add(request):
    form = DoctorScheduleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        schedule = form.save()
        messages.success(
            request, f"Schedule added for {schedule.doctor.full_name} on {schedule.date}."
        )
        return redirect("dashboard:schedule_list")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(
        request,
        "dashboard/schedule_form.html",
        {"form": form, "title": "Add schedule"},
    )


@admin_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    form = DoctorScheduleForm(request.POST or None, instance=schedule)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Schedule updated.")
        return redirect("dashboard:schedule_list")
    return render(
        request,
        "dashboard/schedule_form.html",
        {"form": form, "title": "Edit schedule", "schedule": schedule},
    )


@admin_required
def schedule_toggle(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if request.method == "POST":
        schedule.is_available = not schedule.is_available
        schedule.save(update_fields=["is_available"])
        state = "available" if schedule.is_available else "unavailable"
        messages.success(request, f"Schedule marked {state}.")
    return redirect("dashboard:schedule_list")


@admin_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if request.method == "POST":
        schedule.delete()
        messages.info(request, "Schedule deleted.")
    return redirect("dashboard:schedule_list")


# ------------------------------------------------------------ appointments


@admin_required
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        "doctor", "schedule", "patient"
    ).all()
    status = request.GET.get("status", "").strip()
    query = request.GET.get("q", "").strip()
    if status:
        appointments = appointments.filter(status=status)
    if query:
        appointments = appointments.filter(
            Q(reference__icontains=query)
            | Q(patient_name__icontains=query)
            | Q(doctor__full_name__icontains=query)
        )
    page = Paginator(appointments, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/appointment_list.html",
        {
            "page_obj": page,
            "appointments": page.object_list,
            "statuses": Appointment.Status.choices,
            "status": status,
            "query": query,
        },
    )


@admin_required
def appointment_confirm(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        if appointment.status == Appointment.Status.CONFIRMED:
            messages.info(request, "Appointment is already confirmed.")
        else:
            appointment.mark_confirmed()
            send_appointment_confirmed_email(appointment)
            messages.success(
                request, f"Appointment {appointment.reference} confirmed."
            )
    return redirect(request.POST.get("next") or "dashboard:appointment_list")


@admin_required
def appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in Appointment.Status.values:
            appointment.status = status
            appointment.save()
            if status == Appointment.Status.CONFIRMED:
                send_appointment_confirmed_email(appointment)
            messages.success(
                request,
                f"Appointment {appointment.reference} set to {appointment.get_status_display()}.",
            )
        else:
            messages.error(request, "Unknown appointment status.")
    return redirect("dashboard:appointment_list")


# --------------------------------------------------------------- medicines


@admin_required
def medicine_list(request):
    medicines = Medicine.objects.select_related("category").all()
    query = request.GET.get("q", "").strip()
    stock_filter = request.GET.get("stock", "").strip()
    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )
    if stock_filter == "out":
        medicines = medicines.filter(stock=0)
    elif stock_filter == "low":
        medicines = medicines.filter(stock__gt=0, stock__lte=10)
    page = Paginator(medicines, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/medicine_list.html",
        {
            "page_obj": page,
            "medicines": page.object_list,
            "query": query,
            "stock_filter": stock_filter,
        },
    )


@admin_required
def medicine_add(request):
    form = MedicineForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        medicine = form.save()
        messages.success(request, f"Medicine {medicine.name} added.")
        return redirect("dashboard:medicine_list")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(
        request,
        "dashboard/medicine_form.html",
        {"form": form, "title": "Add medicine", "medicine": None},
    )


@admin_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, request.FILES or None, instance=medicine)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Medicine {medicine.name} updated.")
        return redirect("dashboard:medicine_list")
    return render(
        request,
        "dashboard/medicine_form.html",
        {"form": form, "title": f"Edit {medicine.name}", "medicine": medicine},
    )


@admin_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        name = medicine.name
        medicine.delete()
        messages.info(request, f"Medicine {name} removed.")
    return redirect("dashboard:medicine_list")


@admin_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Category {category.name} added.")
        return redirect("dashboard:medicine_add")
    return render(
        request,
        "dashboard/category_form.html",
        {"form": form, "categories": Category.objects.all()},
    )


# ------------------------------------------------------------------ orders


@admin_required
def order_list(request):
    orders = Order.objects.prefetch_related("items").all()
    status = request.GET.get("status", "").strip()
    query = request.GET.get("q", "").strip()
    if status:
        orders = orders.filter(status=status)
    if query:
        orders = orders.filter(
            Q(order_id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(email__icontains=query)
        )
    page = Paginator(orders, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/order_list.html",
        {
            "page_obj": page,
            "orders": page.object_list,
            "statuses": Order.Status.choices,
            "status": status,
            "query": query,
        },
    )


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_id=order_id)
    return render(
        request,
        "dashboard/order_detail.html",
        {"order": order, "form": OrderStatusForm(instance=order)},
    )


@admin_required
def order_status_update(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            send_order_status_email(order)
            messages.success(
                request, f"Order {order.order_id} is now {order.get_status_display()}."
            )
        else:
            messages.error(request, "Unknown order status.")
    return redirect(request.POST.get("next") or "dashboard:order_list")
