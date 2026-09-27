"""Transactional email helpers.

Emails never raise: delivery problems are logged so user-facing flows keep working.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _send(subject: str, template: str, context: dict, recipient: str | None) -> bool:
    if not recipient:
        return False
    body = render_to_string(template, {**context, "settings": settings})
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception:  # noqa: BLE001 - email must never break a request
        logger.exception("Failed to send email to %s", recipient)
        return False


def send_welcome_email(user) -> bool:
    return _send(
        f"Welcome to {settings.SITE_NAME}",
        "emails/welcome.txt",
        {"user": user},
        user.email,
    )


def send_appointment_booked_email(appointment) -> bool:
    return _send(
        f"Appointment {appointment.reference} received",
        "emails/appointment_booked.txt",
        {"appointment": appointment},
        appointment.patient_email or appointment.patient.email,
    )


def send_appointment_confirmed_email(appointment) -> bool:
    return _send(
        f"Appointment {appointment.reference} confirmed",
        "emails/appointment_confirmed.txt",
        {"appointment": appointment},
        appointment.patient_email or appointment.patient.email,
    )


def send_order_placed_email(order) -> bool:
    return _send(
        f"Order {order.order_id} confirmed",
        "emails/order_placed.txt",
        {"order": order},
        order.email,
    )


def send_contact_email(data: dict) -> bool:
    return _send(
        f"Contact form: {data['subject']}",
        "emails/contact.txt",
        {"data": data},
        settings.SUPPORT_EMAIL,
    )


def send_order_status_email(order) -> bool:
    return _send(
        f"Order {order.order_id} is now {order.get_status_display()}",
        "emails/order_status.txt",
        {"order": order},
        order.email,
    )
