import re
import random
import string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string
from django.conf import settings


def validate_registration(email, password, confirm_password):
    errors = []

    try:
        validate_email(email)
    except ValidationError:
        errors.append("Please enter a valid email address.")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    try:
        validate_password(password)
    except ValidationError as exc:
        errors.extend(exc.messages)

    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors


def normalize_email_for_account_match(email):
    normalized_email = email.strip().lower()

    if "@" not in normalized_email:
        return normalized_email

    local_part, domain = normalized_email.rsplit("@", 1)

    if domain == "googlemail.com":
        domain = "gmail.com"

    if domain == "gmail.com":
        local_part = local_part.split("+", 1)[0].replace(".", "")

    return f"{local_part}@{domain}"


def email_already_registered(email):
    submitted_email = email.strip().lower()
    submitted_match_email = normalize_email_for_account_match(submitted_email)

    for username, user_email in User.objects.values_list("username", "email"):
        existing_values = [
            value.strip().lower()
            for value in (username, user_email)
            if value
        ]

        for existing_value in existing_values:
            if existing_value == submitted_email:
                return True

            if (
                normalize_email_for_account_match(existing_value)
                == submitted_match_email
            ):
                return True

    return False


def generate_order_id():
    suffix = "".join(random.choices(string.digits, k=4))
    return f"HC-{suffix}"


def send_templated_email(subject, template_name, context, recipient_list):
    html_content = render_to_string(template_name, context)
    text_content = render_to_string(template_name.replace(".html", ".txt"), context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
