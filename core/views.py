from django.contrib import messages
from django.shortcuts import redirect, render

from doctors.models import Doctor, Specialization
from pharmacy.models import Medicine

from .emails import send_contact_email
from .forms import ContactForm


def home(request):
    return render(
        request,
        "core/home.html",
        {
            "specializations": Specialization.objects.all()[:6],
            "doctors": Doctor.objects.filter(is_active=True).select_related(
                "specialization"
            )[:4],
            "medicines": Medicine.objects.filter(is_active=True, stock__gt=0)[:4],
        },
    )


def about(request):
    return render(request, "core/about.html")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        send_contact_email(form.cleaned_data)
        messages.success(request, "Thanks for reaching out. We will reply shortly.")
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)
