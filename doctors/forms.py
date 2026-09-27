from django import forms
from django.utils import timezone

from .models import Appointment, Doctor, DoctorSchedule, Specialization


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "full_name",
            "specialization",
            "qualification",
            "experience_years",
            "gender",
            "email",
            "phone",
            "consultation_fee",
            "bio",
            "image",
            "is_active",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check")
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-file")
                field.widget.attrs.setdefault("accept", "image/*")
            else:
                field.widget.attrs.setdefault("class", "form-input")

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and getattr(image, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Image must be 5 MB or smaller.")
        return image


class DoctorImageForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["image"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={"class": "form-file", "accept": "image/*"}
            )
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Please choose an image file.")
        if getattr(image, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Image must be 5 MB or smaller.")
        return image


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ["name", "icon", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = [
            "doctor",
            "date",
            "start_time",
            "end_time",
            "slot_limit",
            "room",
            "is_available",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)
        for name, field in self.fields.items():
            css = "form-check" if isinstance(field.widget, forms.CheckboxInput) else "form-input"
            field.widget.attrs.setdefault("class", css)

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_time"), cleaned.get("end_time")
        date = cleaned.get("date")
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after the start time.")
        if date and date < timezone.localdate():
            raise forms.ValidationError("Schedule date cannot be in the past.")
        return cleaned


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["schedule", "patient_name", "patient_phone", "patient_email", "reason"]
        widgets = {"reason": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, doctor: Doctor | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor
        if doctor is not None:
            self.fields["schedule"].queryset = doctor.schedules.filter(
                is_available=True, date__gte=timezone.localdate()
            )
        self.fields["schedule"].label = "Available slot"
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-input")

    def clean_schedule(self):
        schedule = self.cleaned_data["schedule"]
        if not schedule.is_bookable:
            raise forms.ValidationError("That slot is no longer available.")
        return schedule
