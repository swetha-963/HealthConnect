from django.conf import settings

from pharmacy.models import Cart


def site_context(request):
    cart_count = 0
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        cart = Cart.objects.filter(user=user).prefetch_related("items").first()
        if cart:
            cart_count = cart.items_count
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SUPPORT_EMAIL": settings.SUPPORT_EMAIL,
        "SUPPORT_PHONE": settings.SUPPORT_PHONE,
        "CURRENCY": settings.CURRENCY_SYMBOL,
        "FREE_DELIVERY_THRESHOLD": settings.FREE_DELIVERY_THRESHOLD,
        "cart_count": cart_count,
    }
