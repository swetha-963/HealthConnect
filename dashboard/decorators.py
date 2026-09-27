from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    """Allow only authenticated administrators into the dashboard."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if not user.is_admin_user:
            messages.error(request, "You do not have access to the admin dashboard.")
            return redirect("core:home")
        return view_func(request, *args, **kwargs)

    return _wrapped
