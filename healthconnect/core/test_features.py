from datetime import date, time

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import AdminUser, Appointment, Doctor, DoctorSchedule, Medicine, Order


class FeatureViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="patient@example.com",
            email="patient@example.com",
            password="StrongPass!123",
        )
        self.admin = AdminUser.objects.create(
            email="admin@example.com",
            password=make_password("AdminPass!123"),
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Rao",
            specialization="Cardiology",
            email="doctor@example.com",
            fee="500.00",
            experience=8,
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=date.today(),
            time=time(10, 0),
        )
        self.paracetamol = Medicine.objects.create(
            name="Paracetamol",
            description="Fever and pain relief",
            price="25.00",
            stock=10,
        )
        self.empty_item = Medicine.objects.create(
            name="Vitamin D",
            description="Supplement",
            price="350.00",
            stock=0,
        )

    def test_medicine_finder_filters_by_query_and_stock(self):
        response = self.client.get(
            reverse("medicine_finder"),
            {
                "q": "pain",
                "in_stock": "on",
            },
        )

        self.assertContains(response, "Paracetamol")
        self.assertNotContains(response, "Vitamin D")

    def test_health_tools_returns_bmi_result(self):
        response = self.client.post(
            reverse("health_tools"),
            {
                "tool": "bmi",
                "weight_kg": "70",
                "height_cm": "175",
            },
        )

        self.assertContains(response, "BMI Result")
        self.assertContains(response, "22.9")

    def test_patient_dashboard_requires_login(self):
        response = self.client.get(reverse("patient_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_patient_dashboard_shows_summary(self):
        self.client.login(
            username="patient@example.com",
            password="StrongPass!123",
        )
        Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            schedule=self.schedule,
            date=date.today(),
            time=time(10, 0),
        )
        Order.objects.create(
            user=self.user,
            medicine=self.paracetamol,
        )

        response = self.client.get(reverse("patient_dashboard"))

        self.assertContains(response, "Patient Dashboard")
        self.assertContains(response, "Dr. Rao")
        self.assertContains(response, "Paracetamol")

    def test_admin_insights_uses_custom_admin_session(self):
        session = self.client.session
        session["admin_id"] = self.admin.id
        session["admin_email"] = self.admin.email
        session.save()

        response = self.client.get(reverse("admin_insights"))

        self.assertContains(response, "Insights")
        self.assertContains(response, "Low Stock Inventory")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_register_requires_email_otp_and_emails_submitted_address(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "New.User@gmail.com",
                "password": "StrongPass!123",
                "confirm_password": "StrongPass!123",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="new.user@gmail.com")

        self.assertFalse(user.is_active)
        self.assertEqual(user.email, "new.user@gmail.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new.user@gmail.com"])
        self.assertEqual(
            mail.outbox[0].subject,
            "Your HealthConnect verification code",
        )
        self.assertIn("No Google account data was accessed", mail.outbox[0].body)
        self.assertRegex(mail.outbox[0].body, r"\b\d{6}\b")

    def test_register_rejects_existing_gmail_alias(self):
        User.objects.create_user(
            username="swethabiju215@gmail.com",
            email="swethabiju215@gmail.com",
            password="StrongPass!123",
        )

        response = self.client.post(
            reverse("register"),
            {
                "email": "swetha.biju215+healthconnect@gmail.com",
                "password": "StrongPass!123",
                "confirm_password": "StrongPass!123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            User.objects.filter(
                username="swetha.biju215+healthconnect@gmail.com"
            ).exists()
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_verify_email_activates_account_without_extra_email(self):
        user = User.objects.create_user(
            username="verify-me@example.com",
            email="verify-me@example.com",
            password="StrongPass!123",
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse("verify_email", args=[uid, token]),
            HTTP_USER_AGENT="HealthConnect Test Browser",
            REMOTE_ADDR="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()

        self.assertTrue(user.is_active)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_login_sends_email_to_user(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "patient@example.com",
                "password": "StrongPass!123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["patient@example.com"])
        self.assertEqual(
            mail.outbox[0].subject,
            "New sign-in to your HealthConnect account",
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_booking_sends_email_to_doctor_and_user(self):
        self.client.login(
            username="patient@example.com",
            password="StrongPass!123",
        )

        response = self.client.post(
            reverse("book", args=[self.doctor.id]),
            {
                "schedule_id": self.schedule.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["doctor@example.com"])
        self.assertEqual(mail.outbox[1].to, ["patient@example.com"])
        self.assertEqual(
            mail.outbox[1].subject,
            "Appointment Request Received - HealthConnect",
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_order_sends_email_to_user(self):
        self.client.login(
            username="patient@example.com",
            password="StrongPass!123",
        )
        mail.outbox = []

        response = self.client.post(
            reverse("order", args=[self.paracetamol.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["patient@example.com"])
        self.assertEqual(
            mail.outbox[0].subject,
            "HealthConnect Order Confirmation",
        )
