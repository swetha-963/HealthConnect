from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a HealthConnect test email using the configured SMTP settings."

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            nargs="?",
            help="Email address to receive the test message.",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"] or settings.EMAIL_HOST_USER

        if not settings.EMAIL_HOST_USER:
            raise CommandError("EMAIL_HOST_USER is not configured in .env.")

        if not settings.EMAIL_HOST_PASSWORD:
            raise CommandError("EMAIL_HOST_PASSWORD is not configured in .env.")

        if "your" in settings.EMAIL_HOST_PASSWORD.lower():
            raise CommandError(
                "EMAIL_HOST_PASSWORD still looks like a placeholder. "
                "Use a real Gmail app password."
            )

        if not recipient:
            raise CommandError(
                "No recipient supplied and EMAIL_HOST_USER is empty."
            )

        sent = send_mail(
            subject="HealthConnect SMTP Test",
            message=(
                "This is a test email from HealthConnect. "
                "If you received this, SMTP is configured correctly."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if sent != 1:
            raise CommandError("Django did not report a successful send.")

        self.stdout.write(
            self.style.SUCCESS(f"Test email sent to {recipient}.")
        )
