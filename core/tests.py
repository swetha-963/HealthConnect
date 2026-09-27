"""Public pages and the contact form."""

from django.core import mail
from django.test import TestCase
from django.urls import reverse


class PublicPageTests(TestCase):
    def test_public_pages_render(self):
        for name in ("core:home", "core:about", "core:contact"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_contact_form_sends_email(self):
        mail.outbox.clear()
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Sam Taylor",
                "email": "sam@example.com",
                "subject": "Appointment question",
                "message": "Do you offer evening slots?",
            },
        )
        self.assertRedirects(response, reverse("core:contact"))
        self.assertEqual(len(mail.outbox), 1)

    def test_404_page(self):
        self.assertEqual(self.client.get("/definitely-missing/").status_code, 404)
