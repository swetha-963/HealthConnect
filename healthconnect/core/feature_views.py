import csv
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render

from .decorators import admin_required
from .models import Appointment, DoctorSchedule, Medicine, Order


def _positive_decimal(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None

    if number <= 0:
        return None

    return number


@login_required
def patient_dashboard(request):
    today = date.today()
    appointments = Appointment.objects.filter(
        user=request.user
    ).select_related(
        "doctor",
        "schedule",
    )
    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        "medicine"
    )

    context = {
        "upcoming_appointments": appointments.filter(
            date__gte=today
        ).order_by(
            "date",
            "time",
        )[:5],
        "recent_orders": orders.order_by("-created_at")[:5],
        "total_appointments": appointments.count(),
        "pending_appointments": appointments.filter(confirmed=False).count(),
        "active_orders": orders.exclude(
            status__in=["DELIVERED", "CANCELLED"]
        ).count(),
        "recommended_medicines": Medicine.objects.filter(
            stock__gt=0
        ).exclude(
            orders__user=request.user
        ).order_by(
            "name"
        )[:4],
    }

    return render(
        request,
        "user/patient_dashboard.html",
        context,
    )


def medicine_finder(request):
    query = request.GET.get("q", "").strip()
    max_price = _positive_decimal(request.GET.get("max_price"))
    in_stock_only = request.GET.get("in_stock") == "on"

    medicines = Medicine.objects.all()

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if max_price is not None:
        medicines = medicines.filter(price__lte=max_price)

    if in_stock_only:
        medicines = medicines.filter(stock__gt=0)

    medicines = medicines.order_by("name")

    return render(
        request,
        "user/medicine_finder.html",
        {
            "medicines": medicines,
            "query": query,
            "max_price": request.GET.get("max_price", "").strip(),
            "in_stock_only": in_stock_only,
            "result_count": medicines.count(),
            "stock_count": medicines.filter(stock__gt=0).count(),
        },
    )


def health_tools(request):
    result = None
    error = None

    if request.method == "POST":
        tool = request.POST.get("tool")

        if tool == "bmi":
            weight = _positive_decimal(request.POST.get("weight_kg"))
            height = _positive_decimal(request.POST.get("height_cm"))

            if weight is None or height is None:
                error = "Enter a valid weight and height."
            else:
                height_m = height / Decimal("100")
                bmi = weight / (height_m * height_m)
                bmi_value = bmi.quantize(Decimal("0.1"))

                if bmi < Decimal("18.5"):
                    category = "Below healthy range"
                elif bmi < Decimal("25"):
                    category = "Healthy range"
                elif bmi < Decimal("30"):
                    category = "Above healthy range"
                else:
                    category = "High range"

                result = {
                    "tool": "bmi",
                    "title": "BMI Result",
                    "primary": bmi_value,
                    "secondary": category,
                }

        elif tool == "hydration":
            weight = _positive_decimal(request.POST.get("hydration_weight_kg"))
            activity_minutes = request.POST.get("activity_minutes") or "0"

            try:
                activity = Decimal(str(activity_minutes))
            except InvalidOperation:
                activity = Decimal("-1")

            if weight is None or activity < 0:
                error = "Enter a valid weight and activity time."
            else:
                daily_liters = (
                    (weight * Decimal("35"))
                    + ((activity / Decimal("30")) * Decimal("350"))
                ) / Decimal("1000")

                result = {
                    "tool": "hydration",
                    "title": "Daily Water Target",
                    "primary": f"{daily_liters.quantize(Decimal('0.1'))} L",
                    "secondary": "Adjust for climate, medical advice, and thirst.",
                }

        elif tool == "reminder":
            medicine_name = request.POST.get("medicine_name", "").strip()
            start_time = request.POST.get("start_time", "")

            try:
                doses = int(request.POST.get("doses_per_day", "0"))
                base_time = datetime.strptime(start_time, "%H:%M")
            except ValueError:
                doses = 0
                base_time = None

            if not medicine_name or not base_time or not 1 <= doses <= 6:
                error = "Enter a medicine name, start time, and 1 to 6 doses."
            else:
                interval = 24 / doses
                schedule = [
                    (base_time + timedelta(hours=interval * index)).strftime(
                        "%I:%M %p"
                    )
                    for index in range(doses)
                ]

                result = {
                    "tool": "reminder",
                    "title": f"{medicine_name} Reminder Plan",
                    "primary": f"{doses} dose{'s' if doses != 1 else ''} daily",
                    "items": schedule,
                    "secondary": "Use only with the timing prescribed by your clinician.",
                }

    return render(
        request,
        "user/health_tools.html",
        {
            "result": result,
            "error": error,
        },
    )


@admin_required
def admin_insights(request):
    low_stock_threshold = 5
    order_status_counts = []

    status_labels = dict(Order.STATUS_CHOICES)
    for row in Order.objects.values("status").annotate(
        total=Count("id")
    ).order_by(
        "status"
    ):
        order_status_counts.append(
            {
                "status": row["status"],
                "label": status_labels.get(row["status"], row["status"]),
                "total": row["total"],
            }
        )

    context = {
        "low_stock_threshold": low_stock_threshold,
        "low_stock_medicines": Medicine.objects.filter(
            stock__lte=low_stock_threshold
        ).order_by(
            "stock",
            "name",
        )[:10],
        "pending_appointments": Appointment.objects.filter(
            confirmed=False
        ).select_related(
            "user",
            "doctor",
        ).order_by(
            "date",
            "time",
        )[:10],
        "next_available_slots": DoctorSchedule.objects.filter(
            is_available=True,
            date__gte=date.today(),
        ).select_related(
            "doctor"
        ).order_by(
            "date",
            "time",
        )[:10],
        "top_medicines": Medicine.objects.annotate(
            order_count=Count("orders")
        ).filter(
            order_count__gt=0
        ).order_by(
            "-order_count",
            "name",
        )[:8],
        "order_status_counts": order_status_counts,
        "estimated_revenue": Order.objects.exclude(
            status="CANCELLED"
        ).aggregate(
            total=Sum("medicine__price")
        )["total"] or Decimal("0"),
    }

    return render(
        request,
        "admin/insights.html",
        context,
    )


@admin_required
def export_orders_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="healthconnect-orders.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "Order ID",
            "User Email",
            "Medicine",
            "Price",
            "Status",
            "Created At",
        ]
    )

    for order in Order.objects.select_related(
        "user",
        "medicine",
    ).order_by(
        "-created_at"
    ):
        writer.writerow(
            [
                order.order_id,
                order.user.email,
                order.medicine.name,
                order.medicine.price,
                order.get_status_display(),
                order.created_at.isoformat(),
            ]
        )

    return response


@admin_required
def export_appointments_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="healthconnect-appointments.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "Patient Email",
            "Doctor",
            "Date",
            "Time",
            "Confirmed",
            "Created At",
        ]
    )

    for appointment in Appointment.objects.select_related(
        "user",
        "doctor",
    ).order_by(
        "-created_at"
    ):
        writer.writerow(
            [
                appointment.user.email,
                appointment.doctor.name,
                appointment.date.isoformat(),
                appointment.time.strftime("%H:%M"),
                "Yes" if appointment.confirmed else "No",
                appointment.created_at.isoformat(),
            ]
        )

    return response
