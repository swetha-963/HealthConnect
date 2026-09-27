from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from core.emails import send_welcome_email

from .forms import LoginForm, ProfileForm, RegisterForm


def _post_login_redirect(request, user) -> str:
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return next_url
    if user.is_admin_user:
        return reverse("dashboard:home")
    return reverse("core:home")


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_post_login_redirect(request, request.user))

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.display_name}!")
        return redirect(_post_login_redirect(request, user))
    if request.method == "POST":
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        send_welcome_email(user)
        login(request, user)
        messages.success(request, "Your HealthConnect account is ready.")
        return redirect("core:home")
    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("core:home")


@login_required
def profile_view(request):
    form = ProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})
