"""Patient-facing doctor browsing and appointment booking."""

import datetime as dt
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Doctor, DoctorSchedule, Specialization

User = get_user_model()


class DoctorBookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="patient", email="patient@example.com", password="patient12345"
        )
        self.specialization = Specialization.objects.create(name="Cardiology")
        self.doctor = Doctor.objects.create(
            full_name="Dr. Anika Rao",
            specialization=self.specialization,
            qualification="MBBS, MD",
            experience_years=10,
            consultation_fee=Decimal("90.00"),
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=timezone.localdate() + dt.timedelta(days=3),
            start_time=dt.time(9, 0),
            end_time=dt.time(12, 0),
            slot_limit=2,
        )

    def test_doctor_list_and_detail_public(self):
        self.assertEqual(self.client.get(reverse("doctors:list")).status_code, 200)
        detail = self.client.get(reverse("doctors:detail", args=[self.doctor.slug]))
        self.assertContains(detail, "Dr. Anika Rao")

    def test_booking_requires_login(self):
        response = self.client.get(reverse("doctors:book", args=[self.doctor.slug]))
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_book_appointment_creates_pending_and_emails(self):
        self.client.login(username="patient", password="patient12345")
        mail.outbox.clear()
        response = self.client.post(
            reverse("doctors:book", args=[self.doctor.slug]),
            {
                "schedule": self.schedule.pk,
                "patient_name": "Sam Taylor",
                "patient_phone": "+1 555 0100",
                "patient_email": "patient@example.com",
                "reason": "Chest pain check-up.",
            },
        )
        appointment = Appointment.objects.get()
        self.assertRedirects(response, reverse("doctors:my_appointments"))
        self.assertTrue(appointment.reference.startswith("APT-"))
        self.assertEqual(appointment.status, Appointment.Status.PENDING)
        self.assertFalse(appointment.confirmed)
        self.assertEqual(len(mail.outbox), 1)

    def test_unavailable_schedule_cannot_be_booked(self):
        self.schedule.is_available = False
        self.schedule.save(update_fields=["is_available"])
        self.client.login(username="patient", password="patient12345")
        response = self.client.post(
            reverse("doctors:book", args=[self.doctor.slug]),
            {
                "schedule": self.schedule.pk,
                "patient_name": "Sam Taylor",
                "patient_phone": "+1 555 0100",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Appointment.objects.exists())

    def test_full_schedule_is_not_bookable(self):
        for index in range(self.schedule.slot_limit):
            Appointment.objects.create(
                patient=self.user,
                doctor=self.doctor,
                schedule=self.schedule,
                patient_name=f"Patient {index}",
                patient_phone="+1 555 0100",
            )
        self.assertFalse(self.schedule.is_bookable)

    def test_patient_can_cancel_own_appointment(self):
        self.client.login(username="patient", password="patient12345")
        appointment = Appointment.objects.create(
            patient=self.user,
            doctor=self.doctor,
            schedule=self.schedule,
            patient_name="Sam Taylor",
            patient_phone="+1 555 0100",
        )
        self.client.post(
            reverse("doctors:cancel_appointment", args=[appointment.reference])
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
