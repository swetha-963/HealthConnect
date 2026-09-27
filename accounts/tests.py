"""Authentication and profile flows."""

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthFlowTests(TestCase):
    def test_register_creates_patient_logs_in_and_emails(self):
        mail.outbox.clear()
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newpatient",
                "first_name": "New",
                "last_name": "Patient",
                "email": "new@example.com",
                "phone": "+1 555 0123",
                "password1": "Str0ngPassw0rd!",
                "password2": "Str0ngPassw0rd!",
            },
            follow=True,
        )
        user = User.objects.get(username="newpatient")
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(len(mail.outbox), 1)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="existing", email="dup@example.com", password="pass12345"
        )
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "another",
                "email": "dup@example.com",
                "password1": "Str0ngPassw0rd!",
                "password2": "Str0ngPassw0rd!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_patient_login_redirects_home(self):
        User.objects.create_user(username="patient", password="patient12345")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "patient", "password": "patient12345"},
        )
        self.assertRedirects(response, reverse("core:home"))

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "nobody", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login_and_updates(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertIn(reverse("accounts:login"), response["Location"])

        user = User.objects.create_user(username="patient", password="patient12345")
        self.client.force_login(user)
        self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Sam",
                "last_name": "Taylor",
                "email": "sam@example.com",
                "phone": "+1 555 0100",
                "address": "42 Maple Street",
                "city": "Springfield",
            },
        )
        user.refresh_from_db()
        self.assertEqual(user.city, "Springfield")

    def test_superuser_gets_admin_role(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin12345"
        )
        self.assertTrue(admin.is_admin_user)
