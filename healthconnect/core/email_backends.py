"""Django email backend that delivers messages through Resend's HTTP API."""

import json
import logging
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """Send Django email messages through Resend without using SMTP."""

    api_url = "https://api.resend.com/emails"
    timeout = 15

    def send_messages(self, email_messages):
        sent_count = 0

        for message in email_messages:
            if not message.recipients():
                continue

            if self._send(message):
                sent_count += 1

        return sent_count

    def _send(self, message):
        api_key = settings.RESEND_API_KEY
        if not api_key:
            error = ImproperlyConfigured(
                "RESEND_API_KEY is required to send email."
            )
            if self.fail_silently:
                logger.error("Resend email delivery is not configured.")
                return False
            raise error

        payload = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": message.to,
            "subject": message.subject,
            "text": message.body,
        }

        for content, mimetype in message.alternatives or []:
            if mimetype == "text/html":
                payload["html"] = content
                break

        if message.cc:
            payload["cc"] = message.cc
        if message.bcc:
            payload["bcc"] = message.bcc
        if message.reply_to:
            payload["reply_to"] = message.reply_to
        if message.extra_headers:
            payload["headers"] = message.extra_headers

        try:
            request = Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urlopen(request, timeout=self.timeout):
                pass
        except Exception:
            if self.fail_silently:
                logger.exception("Resend email delivery failed.")
                return False
            raise

        return True
