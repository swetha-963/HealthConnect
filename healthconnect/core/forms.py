from django import forms
from .models import Doctor, DoctorSchedule, Medicine


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.order_by("name")
        self.fields["doctor"].empty_label = "Select doctor"
        self.fields["doctor"].label_from_instance = lambda doctor: (
            f"{doctor.name} — {doctor.specialization}"
        )

    class Meta:
        model = DoctorSchedule

        fields = [
            "doctor",
            "date",
            "time",
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


class MedicineForm(forms.ModelForm):

    class Meta:
        model = Medicine
        fields = [
            "name",
            "description",
            "price",
            "stock",
            "image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "price": forms.NumberInput(
                attrs={"min": "0", "step": "0.01"}
            ),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }
