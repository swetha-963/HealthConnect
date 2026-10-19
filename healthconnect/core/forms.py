from django import forms
from .models import Doctor, DoctorSchedule


class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = [
            "name",
            "specialization",
            "email",
            "fee",
            "experience",
            "clinic_hospital",
            "profile_image",
        ]

        widgets = {
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*"
                }
            ),
        }


class DoctorScheduleForm(forms.ModelForm):

    class Meta:
        model = DoctorSchedule

        fields = [
            "doctor",
            "date",
            "time",
            "is_available",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),
        }