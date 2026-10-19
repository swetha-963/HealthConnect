from datetime import date
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import (
    AdminUser,
    Doctor,
    DoctorSchedule,
    Appointment,
    Medicine,
    Order,
)

from .forms import DoctorForm, DoctorScheduleForm
from .decorators import admin_required
from .utils import (
    validate_registration,
    generate_order_id,
    send_templated_email,
    email_already_registered,
)


logger = logging.getLogger(__name__)


def send_notification_email(subject, template_name, context, recipient_list):
    try:
        send_templated_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=recipient_list,
        )

        return True

    except Exception:
        logger.exception(
            "Unable to send %s to %s",
            template_name,
            ", ".join(recipient_list),
        )

        return False


def build_account_email_context(request, user, extra_context=None):
    current_time = timezone.localtime()
    browser = request.META.get("HTTP_USER_AGENT", "Unknown browser")
    client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()

    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR", "Unknown")

    context = {
        "user": user,
        "site_name": "HealthConnect",
        "site_url": request.build_absolute_uri("/"),
        "event_time": current_time,
        "browser": browser,
        "client_ip": client_ip,
    }

    if extra_context:
        context.update(extra_context)

    return context


def send_email_verification(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_url = request.build_absolute_uri(
        f"/verify-email/{uid}/{token}/"
    )

    return send_notification_email(
        subject="Verify your HealthConnect email",
        template_name="emails/verify_email.html",
        context=build_account_email_context(
            request,
            user,
            {
                "verification_url": verification_url,
            },
        ),
        recipient_list=[
            user.email
        ],
    )


def send_account_data_notice(request, user):
    return send_notification_email(
        subject="You shared account data with HealthConnect",
        template_name="emails/account_data_notice.html",
        context=build_account_email_context(
            request,
            user,
            {
                "shared_data": [
                    "Email address",
                    "Account verification status",
                ],
            },
        ),
        recipient_list=[
            user.email
        ],
    )


# =========================================================
# USER
# =========================================================

def home(request):
    return render(
        request,
        "user/home.html"
    )


def user_register(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # Validate registration details
        errors = validate_registration(
            email,
            password,
            confirm_password
        )

        if errors:
            for error in errors:
                messages.error(request, error)

            return redirect("register")

        # Check if account already exists
        if email_already_registered(email):

            messages.error(
                request,
                "An account with this email already exists. Please sign in instead."
            )

            return redirect("register")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        user.is_active = False
        user.save(
            update_fields=["is_active"]
        )

        email_sent = send_email_verification(
            request,
            user
        )

        messages.success(
            request,
            "Account created. Please verify your email before signing in."
        )

        if not email_sent:
            messages.warning(
                request,
                "The verification email could not be sent. Please check email settings."
            )

        return redirect("login")

    return render(
        request,
        "user/register.html"
    )





def user_login(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            email_sent = send_notification_email(
                subject="HealthConnect Login Notification",
                template_name="emails/login_success.html",
                context=build_account_email_context(
                    request,
                    user,
                    {
                    "login_time": timezone.localtime(),
                    },
                ),
                recipient_list=[
                    user.email
                ],
            )

            if not email_sent:
                messages.warning(
                    request,
                    "Logged in, but the login email could not be sent. Please check email settings."
                )

            return redirect("home")

        inactive_user = User.objects.filter(
            username=email,
            is_active=False
        ).first()

        if inactive_user and inactive_user.check_password(password):
            email_sent = send_email_verification(
                request,
                inactive_user
            )

            messages.warning(
                request,
                "Please verify your email before signing in. We sent a new verification link."
            )

            if not email_sent:
                messages.warning(
                    request,
                    "The verification email could not be sent. Please check email settings."
                )

            return redirect("login")

        messages.error(
            request,
            "Invalid email or password."
        )

    return render(
        request,
        "user/login.html"
    )


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(
            request,
            "This verification link is invalid or has expired."
        )

        return redirect("login")

    if not user.is_active:
        user.is_active = True
        user.save(
            update_fields=["is_active"]
        )

        send_notification_email(
            subject="Welcome to HealthConnect",
            template_name="emails/account_welcome.html",
            context=build_account_email_context(
                request,
                user,
            ),
            recipient_list=[
                user.email
            ],
        )

        send_account_data_notice(
            request,
            user
        )

    messages.success(
        request,
        "Your email has been verified. You can now sign in."
    )

    return redirect("login")


@login_required
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")


# =========================================================
# DOCTORS
# =========================================================

def doctors_list(request):

    doctors = Doctor.objects.all()

    return render(
        request,
        "user/doctors.html",
        {
            "doctors": doctors
        }
    )


@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        id=doctor_id
    )

    schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        is_available=True,
        date__gte=date.today()
    ).order_by(
        "date",
        "time"
    )

    if request.method == "POST":

        schedule_id = request.POST.get(
            "schedule_id"
        )

        if not schedule_id:
            messages.error(
                request,
                "Please select an appointment slot."
            )

            return redirect(
                "book",
                doctor_id=doctor.id
            )

        with transaction.atomic():

            schedule = DoctorSchedule.objects.select_for_update().filter(
                id=schedule_id,
                doctor=doctor,
                is_available=True,
                date__gte=date.today()
            ).first()

            if not schedule:

                messages.error(
                    request,
                    "This appointment slot is no longer available."
                )

                return redirect(
                    "book",
                    doctor_id=doctor.id
                )

            appointment = Appointment.objects.create(
                user=request.user,
                doctor=doctor,
                schedule=schedule,
                date=schedule.date,
                time=schedule.time,
                confirmed=False
            )

            schedule.is_available = False
            schedule.save(
                update_fields=["is_available"]
            )

        send_notification_email(
            subject="New Appointment Request - HealthConnect",
            template_name="emails/appointment_request.html",
            context={
                "doctor": doctor,
                "patient_email": request.user.email,
                "date": appointment.date,
                "time": appointment.time,
            },
            recipient_list=[
                doctor.email
            ],
        )

        email_sent = send_notification_email(
            subject="Appointment Request Received - HealthConnect",
            template_name="emails/appointment_booked.html",
            context={
                "appointment": appointment,
                "doctor": doctor,
                "user": request.user,
            },
            recipient_list=[
                request.user.email
            ],
        )

        messages.success(
            request,
            "Appointment request submitted successfully."
        )

        if not email_sent:
            messages.warning(
                request,
                "Appointment booked, but the confirmation email could not be sent. Please check email settings."
            )

        return redirect(
            "user_appointments"
        )

    return render(
        request,
        "user/book_appointment.html",
        {
            "doctor": doctor,
            "schedules": schedules,
        }
    )


# =========================================================
# APPOINTMENTS
# =========================================================

@login_required
def user_appointments(request):

    appointments = Appointment.objects.filter(
        user=request.user
    ).select_related(
        "doctor",
        "schedule"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "user/appointments.html",
        {
            "appointments": appointments
        }
    )


# =========================================================
# MEDICINES
# =========================================================

def medicines_list(request):

    medicines = Medicine.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "user/medicines.html",
        {
            "medicines": medicines
        }
    )


@login_required
def confirm_order(request, medicine_id):

    medicine = get_object_or_404(
        Medicine,
        id=medicine_id
    )

    if medicine.stock <= 0:

        messages.error(
            request,
            "This medicine is currently out of stock."
        )

        return redirect("medicines")

    if request.method == "POST":

        with transaction.atomic():

            medicine = Medicine.objects.select_for_update().get(
                id=medicine.id
            )

            if medicine.stock <= 0:

                messages.error(
                    request,
                    "This medicine is currently out of stock."
                )

                return redirect("medicines")

            order = Order.objects.create(
                user=request.user,
                medicine=medicine,
                status="PLACED"
            )

            medicine.stock -= 1

            medicine.save(
                update_fields=["stock"]
            )

        email_sent = send_notification_email(
            subject="HealthConnect Order Confirmation",
            template_name="emails/order_confirmation.html",
            context={
                "medicine": medicine,
                "order": order,
                "user": request.user,
            },
            recipient_list=[
                request.user.email
            ],
        )

        messages.success(
            request,
            f"Order {order.order_id} placed successfully."
        )

        if not email_sent:
            messages.warning(
                request,
                "Order placed, but the confirmation email could not be sent. Please check email settings."
            )

        return redirect(
            "user_orders"
        )

    return render(
        request,
        "user/confirm_order.html",
        {
            "medicine": medicine
        }
    )


@login_required
def user_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        "medicine"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "user/orders.html",
        {
            "orders": orders
        }
    )


# =========================================================
# NEARBY
# =========================================================

# def nearby(request):

#     return render(
#         request,
#         "user/nearby.html",
#         {
#             "google_maps_api_key": getattr(
#                 settings,
#                 "GOOGLE_MAPS_API_KEY",
#                 ""
#             )
#         }
#     )


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    if request.session.get("admin_id"):
        return redirect(
            "admin_dashboard"
        )

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        admin = AdminUser.objects.filter(
            email=email
        ).first()

        if admin and check_password(
            password,
            admin.password
        ):

            request.session["admin_id"] = admin.id
            request.session["admin_email"] = admin.email

            return redirect(
                "admin_dashboard"
            )

        messages.error(
            request,
            "Invalid admin email or password."
        )

    return render(
        request,
        "admin/admin_login.html"
    )


def admin_logout(request):

    request.session.flush()

    messages.success(
        request,
        "Admin logged out successfully."
    )

    return redirect(
        "admin_login"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_required
def admin_dashboard(request):

    doctors_count = Doctor.objects.count()

    schedules_count = DoctorSchedule.objects.count()

    appointments_count = Appointment.objects.count()

    pending_appointments = Appointment.objects.filter(
        confirmed=False
    ).count()

    medicines_count = Medicine.objects.count()

    orders_count = Order.objects.count()

    users_count = User.objects.count()

    recent_appointments = Appointment.objects.select_related(
        "user",
        "doctor"
    ).order_by(
        "-created_at"
    )[:10]

    recent_orders = Order.objects.select_related(
        "user",
        "medicine"
    ).order_by(
        "-created_at"
    )[:10]

    context = {
        "doctors_count": doctors_count,
        "schedules_count": schedules_count,
        "appointments_count": appointments_count,
        "pending_appointments": pending_appointments,
        "medicines_count": medicines_count,
        "orders_count": orders_count,
        "users_count": users_count,
        "recent_appointments": recent_appointments,
        "recent_orders": recent_orders,
    }

    return render(
        request,
        "admin/dashboard.html",
        context
    )


# =========================================================
# ADMIN DOCTORS
# =========================================================

@admin_required
def admin_doctors(request):

    doctors = Doctor.objects.all().prefetch_related(
        "schedules"
    ).order_by(
        "name"
    )

    return render(
        request,
        "admin/doctors.html",
        {
            "doctors": doctors
        }
    )


@admin_required
def add_doctor(request):

    if request.method == "POST":

        form = DoctorForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Doctor added successfully."
            )

            return redirect(
                "admin_doctors"
            )

    else:

        form = DoctorForm()

    return render(
        request,
        "admin/add_doctor.html",
        {
            "form": form
        }
    )


# =========================================================
# ADMIN SCHEDULES
# =========================================================

@admin_required
def add_schedule(request):

    if request.method == "POST":

        form = DoctorScheduleForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Doctor schedule added successfully."
            )

            return redirect(
                "admin_schedules"
            )

    else:

        form = DoctorScheduleForm()

    return render(
        request,
        "admin/add_schedule.html",
        {
            "form": form
        }
    )


@admin_required
def admin_schedules(request):

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        schedule_id = request.POST.get(
            "schedule_id"
        )

        if action == "delete":

            schedule = get_object_or_404(
                DoctorSchedule,
                id=schedule_id
            )

            if schedule.is_available:

                schedule.delete()

                messages.success(
                    request,
                    "Schedule deleted successfully."
                )

            else:

                messages.error(
                    request,
                    "Booked schedules cannot be deleted."
                )

            return redirect(
                "admin_schedules"
            )

    schedules = DoctorSchedule.objects.select_related(
        "doctor"
    ).order_by(
        "date",
        "time"
    )

    return render(
        request,
        "admin/schedules.html",
        {
            "schedules": schedules
        }
    )


# =========================================================
# ADMIN APPOINTMENTS
# =========================================================

@admin_required
def admin_appointments(request):

    if request.method == "POST":

        appointment_id = request.POST.get(
            "appointment_id"
        )

        action = request.POST.get(
            "action"
        )

        appointment = get_object_or_404(
            Appointment.objects.select_related(
                "doctor",
                "user",
                "schedule"
            ),
            id=appointment_id
        )

        if action == "confirm":

            appointment.confirmed = True

            appointment.save(
                update_fields=["confirmed"]
            )

            email_sent = send_notification_email(
                subject="Appointment Confirmed - HealthConnect",
                template_name="emails/appointment_confirmed.html",
                context={
                    "appointment": appointment,
                    "doctor": appointment.doctor,
                },
                recipient_list=[
                    appointment.user.email
                ],
            )

            messages.success(
                request,
                "Appointment confirmed successfully."
            )

            if not email_sent:
                messages.warning(
                    request,
                    "Appointment confirmed, but the patient email could not be sent. Please check email settings."
                )

        elif action == "reject":

            if appointment.schedule:

                appointment.schedule.is_available = True

                appointment.schedule.save(
                    update_fields=["is_available"]
                )

            appointment.delete()

            messages.success(
                request,
                "Appointment rejected."
            )

        elif action == "cancel":

            if appointment.schedule:

                appointment.schedule.is_available = True

                appointment.schedule.save(
                    update_fields=["is_available"]
                )

            appointment.confirmed = False

            appointment.save(
                update_fields=["confirmed"]
            )

            messages.success(
                request,
                "Appointment cancelled."
            )

        return redirect(
            "admin_appointments"
        )

    appointments = Appointment.objects.select_related(
        "user",
        "doctor",
        "schedule"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "admin/appointments.html",
        {
            "appointments": appointments
        }
    )


# =========================================================
# ADMIN MEDICINES
# =========================================================

@admin_required
def admin_medicines(request):

    medicines = Medicine.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "admin/medicines.html",
        {
            "medicines": medicines
        }
    )


@admin_required
def add_medicine(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get(
            "price",
            "0"
        )

        stock = request.POST.get(
            "stock",
            "0"
        )

        image = request.FILES.get(
            "image"
        )

        if not name:

            messages.error(
                request,
                "Medicine name is required."
            )

            return redirect(
                "add_medicine"
            )

        try:

            price = float(price)
            stock = int(stock)

            if price < 0 or stock < 0:
                raise ValueError

        except ValueError:

            messages.error(
                request,
                "Enter valid price and stock values."
            )

            return redirect(
                "add_medicine"
            )

        Medicine.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )

        messages.success(
            request,
            "Medicine added successfully."
        )

        return redirect(
            "admin_medicines"
        )

    return render(
        request,
        "admin/add_medicine.html"
    )


# =========================================================
# ADMIN ORDERS
# =========================================================

@admin_required
def admin_orders(request):

    if request.method == "POST":

        order_id = request.POST.get(
            "order_id"
        )

        status = request.POST.get(
            "status"
        )

        order = get_object_or_404(
            Order,
            id=order_id
        )

        valid_statuses = dict(
            Order.STATUS_CHOICES
        )

        if status not in valid_statuses:

            messages.error(
                request,
                "Invalid order status."
            )

            return redirect(
                "admin_orders"
            )

        order.status = status

        order.save(
            update_fields=["status"]
        )

        messages.success(
            request,
            f"Order {order.order_id} updated."
        )

        return redirect(
            "admin_orders"
        )

    orders = Order.objects.select_related(
        "user",
        "medicine"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "admin/orders.html",
        {
            "orders": orders
        }
    )
