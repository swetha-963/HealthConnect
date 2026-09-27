"""End-to-end coverage for the admin dashboard workflows."""

import datetime as dt
import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from doctors.models import Appointment, Doctor, DoctorSchedule, Specialization
from pharmacy.models import Category, Medicine, Order, OrderItem

User = get_user_model()


def make_image(name="doctor.png", size=(80, 80)) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, (14, 165, 233)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT="/tmp/healthconnect-test-media")
class DashboardWorkflowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin12345"
        )
        self.patient = User.objects.create_user(
            username="patient", email="patient@example.com", password="patient12345"
        )
        self.specialization = Specialization.objects.create(name="Cardiology")
        self.doctor = Doctor.objects.create(
            full_name="Dr. Anika Rao",
            specialization=self.specialization,
            qualification="MBBS, MD",
            experience_years=10,
            consultation_fee=Decimal("90.00"),
            email="anika@example.com",
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=timezone.localdate() + dt.timedelta(days=2),
            start_time=dt.time(9, 0),
            end_time=dt.time(12, 0),
            slot_limit=5,
        )
        self.category = Category.objects.create(name="Pain Relief")
        self.medicine = Medicine.objects.create(
            name="Paracetamol 500mg",
            category=self.category,
            brand="MediCare",
            price=Decimal("18.50"),
            stock=25,
        )

    def login_admin(self):
        self.assertTrue(self.client.login(username="admin", password="admin12345"))

    # 1. admin login -------------------------------------------------------
    def test_admin_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "admin12345"},
            follow=True,
        )
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_patient_cannot_open_dashboard(self):
        self.client.login(username="patient", password="patient12345")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertIn(reverse("accounts:login"), response["Location"])

    # 2. dashboard ---------------------------------------------------------
    def test_dashboard_overview_renders_stats(self):
        self.login_admin()
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stats"]["doctors"], 1)
        self.assertEqual(response.context["stats"]["medicines"], 1)

    def test_every_dashboard_page_renders(self):
        self.login_admin()
        pages = [
            reverse("dashboard:home"),
            reverse("dashboard:doctor_list"),
            reverse("dashboard:doctor_add"),
            reverse("dashboard:doctor_edit", args=[self.doctor.pk]),
            reverse("dashboard:doctor_image", args=[self.doctor.pk]),
            reverse("dashboard:specialization_add"),
            reverse("dashboard:schedule_list"),
            reverse("dashboard:schedule_add"),
            reverse("dashboard:schedule_edit", args=[self.schedule.pk]),
            reverse("dashboard:appointment_list"),
            reverse("dashboard:medicine_list"),
            reverse("dashboard:medicine_add"),
            reverse("dashboard:medicine_edit", args=[self.medicine.pk]),
            reverse("dashboard:category_add"),
            reverse("dashboard:order_list"),
        ]
        for url in pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    # 3 & 4. add doctor + doctor image -------------------------------------
    def test_add_doctor_with_image(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:doctor_add"),
            {
                "full_name": "Dr. Vikram Shah",
                "specialization": self.specialization.pk,
                "qualification": "MBBS, MD",
                "experience_years": 9,
                "gender": "male",
                "email": "vikram@example.com",
                "phone": "+1 555 0111",
                "consultation_fee": "65.00",
                "bio": "Dermatologist.",
                "is_active": "on",
                "image": make_image(),
            },
        )
        self.assertRedirects(response, reverse("dashboard:doctor_list"))
        doctor = Doctor.objects.get(full_name="Dr. Vikram Shah")
        self.assertTrue(doctor.image)

    def test_update_doctor_image_only(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:doctor_image", args=[self.doctor.pk]),
            {"image": make_image("updated.png")},
        )
        self.assertRedirects(response, reverse("dashboard:doctor_list"))
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.image)

    def test_doctor_image_required(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:doctor_image", args=[self.doctor.pk]), {}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Doctor.objects.get(pk=self.doctor.pk).image)

    # 5 & 6. add / view schedules -----------------------------------------
    def test_add_schedule(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:schedule_add"),
            {
                "doctor": self.doctor.pk,
                "date": (timezone.localdate() + dt.timedelta(days=5)).isoformat(),
                "start_time": "14:00",
                "end_time": "17:00",
                "slot_limit": 6,
                "room": "Room 204",
                "is_available": "on",
            },
        )
        self.assertRedirects(response, reverse("dashboard:schedule_list"))
        self.assertEqual(DoctorSchedule.objects.count(), 2)

    def test_schedule_rejects_invalid_times(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:schedule_add"),
            {
                "doctor": self.doctor.pk,
                "date": (timezone.localdate() + dt.timedelta(days=5)).isoformat(),
                "start_time": "17:00",
                "end_time": "14:00",
                "slot_limit": 6,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DoctorSchedule.objects.count(), 1)

    def test_view_and_filter_schedules(self):
        self.login_admin()
        response = self.client.get(
            reverse("dashboard:schedule_list"), {"availability": "available"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.schedule, list(response.context["schedules"]))

    def test_toggle_schedule_availability(self):
        self.login_admin()
        self.client.post(reverse("dashboard:schedule_toggle", args=[self.schedule.pk]))
        self.schedule.refresh_from_db()
        self.assertFalse(self.schedule.is_available)

    # 7 & 8. view / confirm appointments -----------------------------------
    def make_appointment(self) -> Appointment:
        return Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            schedule=self.schedule,
            patient_name="Sam Taylor",
            patient_phone="+1 555 0100",
            patient_email="patient@example.com",
        )

    def test_view_appointments(self):
        appointment = self.make_appointment()
        self.login_admin()
        response = self.client.get(reverse("dashboard:appointment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(appointment, list(response.context["appointments"]))

    def test_confirm_appointment_sets_flag_and_emails(self):
        appointment = self.make_appointment()
        self.assertFalse(appointment.confirmed)
        self.login_admin()
        mail.outbox.clear()
        self.client.post(reverse("dashboard:appointment_confirm", args=[appointment.pk]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)
        self.assertTrue(appointment.confirmed)
        self.assertIsNotNone(appointment.confirmed_at)
        self.assertEqual(len(mail.outbox), 1)

    # 9, 10. medicines -----------------------------------------------------
    def test_view_medicines_and_low_stock_filter(self):
        Medicine.objects.create(
            name="Ibuprofen", category=self.category, price=Decimal("22"), stock=4
        )
        self.login_admin()
        response = self.client.get(reverse("dashboard:medicine_list"), {"stock": "low"})
        self.assertEqual(
            [m.name for m in response.context["medicines"]], ["Ibuprofen"]
        )

    def test_add_medicine(self):
        self.login_admin()
        response = self.client.post(
            reverse("dashboard:medicine_add"),
            {
                "name": "Vitamin D3",
                "category": self.category.pk,
                "brand": "SunLife",
                "description": "Daily supplement.",
                "price": "25.90",
                "stock": 40,
                "low_stock_threshold": 10,
                "is_active": "on",
                "image": make_image("medicine.png"),
            },
        )
        self.assertRedirects(response, reverse("dashboard:medicine_list"))
        medicine = Medicine.objects.get(name="Vitamin D3")
        self.assertEqual(medicine.stock, 40)
        self.assertTrue(medicine.image)

    # 11, 12. orders -------------------------------------------------------
    def make_order(self) -> Order:
        order = Order.objects.create(
            user=self.patient,
            full_name="Sam Taylor",
            email="patient@example.com",
            phone="+1 555 0100",
            address="42 Maple Street",
            city="Springfield",
            subtotal=Decimal("37.00"),
            delivery_fee=Decimal("4.99"),
            total=Decimal("41.99"),
        )
        OrderItem.objects.create(
            order=order,
            medicine=self.medicine,
            medicine_name=self.medicine.name,
            unit_price=self.medicine.price,
            quantity=2,
        )
        return order

    def test_order_id_generated(self):
        order = self.make_order()
        self.assertTrue(order.order_id.startswith("HC-"))

    def test_view_orders_and_detail(self):
        order = self.make_order()
        self.login_admin()
        self.assertEqual(
            self.client.get(reverse("dashboard:order_list")).status_code, 200
        )
        detail = self.client.get(
            reverse("dashboard:order_detail", args=[order.order_id])
        )
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, order.order_id)

    def test_update_order_status_sends_email(self):
        order = self.make_order()
        self.login_admin()
        mail.outbox.clear()
        response = self.client.post(
            reverse("dashboard:order_status_update", args=[order.order_id]),
            {"status": Order.Status.SHIPPED},
        )
        self.assertRedirects(response, reverse("dashboard:order_list"))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.SHIPPED)
        self.assertEqual(len(mail.outbox), 1)

    # 13. logout -----------------------------------------------------------
    def test_logout(self):
        self.login_admin()
        response = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
