import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Specialization(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=8, default="+", help_text="Short emoji or glyph shown on cards."
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Doctor(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    full_name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    specialization = models.ForeignKey(
        Specialization, on_delete=models.PROTECT, related_name="doctors"
    )
    qualification = models.CharField(max_length=120, help_text="e.g. MBBS, MD")
    experience_years = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="doctors/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name) or "doctor"
            slug = base
            counter = 2
            while Doctor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("doctors:detail", args=[self.slug])

    @property
    def initials(self) -> str:
        parts = [p for p in self.full_name.replace("Dr.", "").split() if p]
        return "".join(p[0].upper() for p in parts[:2]) or "DR"

    @property
    def available_schedules(self):
        return self.schedules.filter(is_available=True, date__gte=timezone.localdate())

    def __str__(self) -> str:
        return self.full_name


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_limit = models.PositiveIntegerField(default=10)
    room = models.CharField(max_length=40, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ("doctor", "date", "start_time")

    @property
    def booked_count(self) -> int:
        return self.appointments.exclude(
            status=Appointment.Status.CANCELLED
        ).count()

    @property
    def seats_left(self) -> int:
        return max(self.slot_limit - self.booked_count, 0)

    @property
    def is_past(self) -> bool:
        return self.date < timezone.localdate()

    @property
    def is_bookable(self) -> bool:
        return self.is_available and not self.is_past and self.seats_left > 0

    def __str__(self) -> str:
        return f"{self.doctor.full_name} - {self.date} {self.start_time:%H:%M}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    schedule = models.ForeignKey(
        DoctorSchedule, on_delete=models.CASCADE, related_name="appointments"
    )
    patient_name = models.CharField(max_length=120)
    patient_phone = models.CharField(max_length=20)
    patient_email = models.EmailField(blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.confirmed = self.status == self.Status.CONFIRMED
        if self.confirmed and self.confirmed_at is None:
            self.confirmed_at = timezone.now()
        if not self.confirmed:
            self.confirmed_at = None
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference() -> str:
        return f"APT-{uuid.uuid4().hex[:8].upper()}"

    def mark_confirmed(self):
        self.status = self.Status.CONFIRMED
        self.save()

    @property
    def status_class(self) -> str:
        return {
            self.Status.PENDING: "badge-warning",
            self.Status.CONFIRMED: "badge-success",
            self.Status.COMPLETED: "badge-info",
            self.Status.CANCELLED: "badge-danger",
        }[self.Status(self.status)]

    def __str__(self) -> str:
        return f"{self.reference} - {self.patient_name} with {self.doctor.full_name}"
