"""Populate the database with demo doctors, schedules, medicines and users."""

import datetime as dt
import os
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from doctors.models import Appointment, Doctor, DoctorSchedule, Specialization
from pharmacy.models import Category, Medicine

User = get_user_model()

SPECIALIZATIONS = [
    ("Cardiology", "H", "Heart and vascular care."),
    ("Dermatology", "S", "Skin, hair and nail treatments."),
    ("Pediatrics", "P", "Care for infants, children and teens."),
    ("Orthopedics", "B", "Bones, joints and sports injuries."),
    ("General Medicine", "G", "Everyday consultations and check-ups."),
    ("Neurology", "N", "Brain and nervous system specialists."),
]

DOCTORS = [
    ("Dr. Anika Rao", "Cardiology", "MBBS, MD (Cardiology)", 14, "female", 90),
    ("Dr. Vikram Shah", "Dermatology", "MBBS, MD (Dermatology)", 9, "male", 65),
    ("Dr. Leah Fernandes", "Pediatrics", "MBBS, DCH", 11, "female", 55),
    ("Dr. Samuel Okoro", "Orthopedics", "MBBS, MS (Ortho)", 16, "male", 100),
    ("Dr. Priya Nair", "General Medicine", "MBBS", 7, "female", 40),
    ("Dr. Daniel Brooks", "Neurology", "MBBS, DM (Neurology)", 18, "male", 120),
]

CATEGORIES = [
    ("Pain Relief", "Analgesics and anti-inflammatory medicines."),
    ("Cold & Flu", "Relief for cough, cold and fever."),
    ("Vitamins & Supplements", "Daily nutrition support."),
    ("Diabetes Care", "Monitoring and treatment essentials."),
    ("First Aid", "Dressings, antiseptics and kits."),
]

MEDICINES = [
    ("Paracetamol 500mg", "Pain Relief", "MediCare", "18.50", 120, False),
    ("Ibuprofen 400mg", "Pain Relief", "HealWell", "22.00", 8, False),
    ("Cough Syrup 100ml", "Cold & Flu", "BreatheEasy", "14.75", 60, False),
    ("Antihistamine Tablets", "Cold & Flu", "ClearAir", "12.30", 0, False),
    ("Vitamin D3 1000 IU", "Vitamins & Supplements", "SunLife", "25.90", 75, False),
    ("Multivitamin Complex", "Vitamins & Supplements", "DailyVita", "31.40", 45, False),
    ("Glucose Test Strips", "Diabetes Care", "GlucoCheck", "45.00", 30, False),
    ("Metformin 500mg", "Diabetes Care", "GlycoMed", "27.60", 25, True),
    ("Adhesive Bandages (50)", "First Aid", "SafeSkin", "9.99", 200, False),
    ("Antiseptic Solution 250ml", "First Aid", "PureCare", "16.20", 6, False),
]


class Command(BaseCommand):
    help = "Seed HealthConnect with demo data (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-appointments",
            action="store_true",
            help="Delete existing demo appointments before seeding.",
        )

    def handle(self, *args, **options):
        admin = self._create_admin()
        patient = self._create_patient()
        self._create_specializations()
        self._create_doctors()
        schedules = self._create_schedules()
        self._create_catalog()
        if options["reset_appointments"]:
            Appointment.objects.filter(patient=patient).delete()
        self._create_appointments(patient, schedules)

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(f"  Admin    : {admin.username} / {self._admin_password()}")
        self.stdout.write(f"  Patient  : {patient.username} / patient12345")

    # ------------------------------------------------------------- helpers

    @staticmethod
    def _admin_password() -> str:
        return os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin12345")

    def _create_admin(self) -> User:
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@healthconnect.local")
        admin, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": "Health",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
                "role": User.Role.ADMIN,
            },
        )
        if created:
            admin.set_password(self._admin_password())
            admin.save()
        return admin

    def _create_patient(self) -> User:
        patient, created = User.objects.get_or_create(
            username="patient",
            defaults={
                "email": "patient@healthconnect.local",
                "first_name": "Sam",
                "last_name": "Taylor",
                "phone": "+1 555 0100",
                "address": "42 Maple Street",
                "city": "Springfield",
            },
        )
        if created:
            patient.set_password("patient12345")
            patient.save()
        return patient

    def _create_specializations(self):
        for name, icon, description in SPECIALIZATIONS:
            Specialization.objects.get_or_create(
                name=name, defaults={"icon": icon, "description": description}
            )

    def _create_doctors(self):
        for name, specialization, qualification, years, gender, fee in DOCTORS:
            Doctor.objects.get_or_create(
                full_name=name,
                defaults={
                    "specialization": Specialization.objects.get(name=specialization),
                    "qualification": qualification,
                    "experience_years": years,
                    "gender": gender,
                    "consultation_fee": Decimal(str(fee)),
                    "email": name.lower().replace("dr. ", "").replace(" ", ".")
                    + "@healthconnect.local",
                    "phone": "+1 555 0110",
                    "bio": f"{name} has {years} years of experience in {specialization.lower()} "
                    "and consults at the HealthConnect central clinic.",
                },
            )

    def _create_schedules(self) -> list[DoctorSchedule]:
        today = timezone.localdate()
        created = []
        for offset, doctor in enumerate(Doctor.objects.all(), start=1):
            for day in (offset, offset + 3):
                schedule, _ = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    date=today + dt.timedelta(days=day),
                    start_time=dt.time(9, 0) if day % 2 else dt.time(14, 0),
                    defaults={
                        "end_time": dt.time(12, 0) if day % 2 else dt.time(17, 0),
                        "slot_limit": 8,
                        "room": f"Room {100 + offset}",
                        "is_available": True,
                    },
                )
                created.append(schedule)
        return created

    def _create_catalog(self):
        for name, description in CATEGORIES:
            Category.objects.get_or_create(name=name, defaults={"description": description})
        for name, category, brand, price, stock, rx in MEDICINES:
            Medicine.objects.get_or_create(
                name=name,
                defaults={
                    "category": Category.objects.get(name=category),
                    "brand": brand,
                    "price": Decimal(price),
                    "stock": stock,
                    "prescription_required": rx,
                    "description": f"{name} supplied by {brand}. Store below 25 C, away from direct sunlight.",
                },
            )

    def _create_appointments(self, patient: User, schedules: list[DoctorSchedule]):
        if Appointment.objects.filter(patient=patient).exists() or not schedules:
            return
        for schedule in schedules[:2]:
            Appointment.objects.create(
                patient=patient,
                doctor=schedule.doctor,
                schedule=schedule,
                patient_name=patient.display_name,
                patient_phone=patient.phone or "+1 555 0100",
                patient_email=patient.email,
                reason="Routine consultation.",
            )
