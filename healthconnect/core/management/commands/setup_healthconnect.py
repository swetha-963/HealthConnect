import os

from django.contrib.auth.hashers import check_password, make_password
from django.core.management.base import BaseCommand, CommandError

from core.models import AdminUser, Doctor, Medicine


class Command(BaseCommand):
    help = "Seed the configured admin, sample doctors, and medicines"

    def handle(self, *args, **options):
        admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "")
        if not admin_email or not admin_password:
            raise CommandError(
                "Set ADMIN_EMAIL and ADMIN_PASSWORD before running this command."
            )

        admin, created = AdminUser.objects.get_or_create(
            email=admin_email,
            defaults={"password": make_password(admin_password)},
        )
        if not created and not check_password(admin_password, admin.password):
            admin.password = make_password(admin_password)
            admin.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user ready: {admin_email}"))

        if not Doctor.objects.exists():
            Doctor.objects.create(
                name="Dr. Anjali Nair",
                specialization="General Physician",
                email="anjali.nair@healthconnect.com",
                fee=500,
                experience=12,
                clinic_hospital="City Care Hospital",
            )
            Doctor.objects.create(
                name="Dr. Rahul Mehta",
                specialization="Cardiologist",
                email="rahul.mehta@healthconnect.com",
                fee=800,
                experience=15,
                clinic_hospital="Heart & Health Clinic",
            )
            self.stdout.write(self.style.SUCCESS("Sample doctors created."))

        if not Medicine.objects.exists():
            medicines = [
                ("Paracetamol 500mg", "Pain relief and fever reducer", 25, 100),
                ("Amoxicillin 250mg", "Antibiotic for bacterial infections", 120, 50),
                ("Cetirizine 10mg", "Allergy and hay fever relief", 35, 80),
                ("Omeprazole 20mg", "Acid reflux and heartburn", 90, 60),
            ]
            for name, desc, price, stock in medicines:
                Medicine.objects.create(name=name, description=desc, price=price, stock=stock)
            self.stdout.write(self.style.SUCCESS("Sample medicines created."))

        self.stdout.write(self.style.SUCCESS("Setup complete."))
