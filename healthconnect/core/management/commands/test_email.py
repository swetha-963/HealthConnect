from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a HealthConnect test email through the configured email backend."

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            nargs="?",
            help="Email address to receive the test message.",
        )

    def handle(self, *args, **options):
        if not settings.RESEND_API_KEY:
            raise CommandError("Set RESEND_API_KEY before testing email delivery.")

        if settings.EMAIL_BACKEND != "core.email_backends.ResendEmailBackend":
            raise CommandError(
                "The configured email backend is not Resend. Remove the local "
                "EMAIL_BACKEND override before running this command."
            )

        recipient = options["recipient"]
        if not recipient:
            raise CommandError(
                "Pass a recipient email address, for example "
                "delivered@resend.dev for a Resend delivery test."
            )

        sent = send_mail(
            subject="HealthConnect Email Test",
            message=(
                "This is a test email from HealthConnect. "
                "If you received this, email delivery is configured correctly."
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
