# from functools import wraps

# from django.shortcuts import redirect


# def admin_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if not request.session.get("admin_id"):
#             return redirect("admin_login")
#         return view_func(request, *args, **kwargs)

#     return wrapper




from functools import wraps
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_id"):
            return redirect("admin_login")

        return view_func(request, *args, **kwargs)

    return wrapper