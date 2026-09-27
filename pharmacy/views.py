from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.emails import send_order_placed_email

from .forms import CheckoutForm
from .models import Cart, CartItem, Category, Medicine, Order, OrderItem


def get_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def medicine_list(request):
    medicines = Medicine.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "").strip()

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
        )
    if category:
        medicines = medicines.filter(category__slug=category)
    if sort == "price_asc":
        medicines = medicines.order_by("price")
    elif sort == "price_desc":
        medicines = medicines.order_by("-price")

    paginator = Paginator(medicines, 12)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "pharmacy/medicine_list.html",
        {
            "page_obj": page,
            "medicines": page.object_list,
            "categories": Category.objects.all(),
            "query": query,
            "active_category": category,
            "sort": sort,
        },
    )


def medicine_detail(request, slug):
    medicine = get_object_or_404(
        Medicine.objects.select_related("category"), slug=slug, is_active=True
    )
    related = (
        Medicine.objects.filter(category=medicine.category, is_active=True)
        .exclude(pk=medicine.pk)[:4]
    )
    return render(
        request,
        "pharmacy/medicine_detail.html",
        {"medicine": medicine, "related_medicines": related},
    )


@login_required
def cart_view(request):
    cart = get_cart(request.user)
    return render(request, "pharmacy/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    if request.method != "POST":
        return redirect(medicine.get_absolute_url())

    try:
        quantity = max(int(request.POST.get("quantity", 1)), 1)
    except ValueError:
        quantity = 1

    if not medicine.in_stock:
        messages.error(request, f"{medicine.name} is out of stock.")
        return redirect(medicine.get_absolute_url())

    cart = get_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, medicine=medicine)
    new_quantity = quantity if created else item.quantity + quantity
    if new_quantity > medicine.stock:
        new_quantity = medicine.stock
        messages.warning(
            request, f"Only {medicine.stock} units of {medicine.name} are available."
        )
    item.quantity = new_quantity
    item.save()
    messages.success(request, f"{medicine.name} added to your cart.")
    return redirect(request.POST.get("next") or "pharmacy:cart")


@login_required
def update_cart_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", item.quantity))
        except ValueError:
            quantity = item.quantity
        if quantity <= 0:
            item.delete()
            messages.info(request, "Item removed from cart.")
        else:
            if quantity > item.medicine.stock:
                quantity = item.medicine.stock
                messages.warning(
                    request, f"Only {item.medicine.stock} units available."
                )
            item.quantity = quantity
            item.save()
            messages.success(request, "Cart updated.")
    return redirect("pharmacy:cart")


@login_required
def remove_cart_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if request.method == "POST":
        item.delete()
        messages.info(request, "Item removed from cart.")
    return redirect("pharmacy:cart")


@login_required
def checkout(request):
    cart = get_cart(request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("pharmacy:medicine_list")

    initial = {
        "full_name": request.user.display_name,
        "email": request.user.email,
        "phone": request.user.phone,
        "address": request.user.address,
        "city": request.user.city,
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            items = list(cart.items.select_related("medicine"))
            for item in items:
                if item.quantity > item.medicine.stock:
                    messages.error(
                        request,
                        f"{item.medicine.name} only has {item.medicine.stock} units left.",
                    )
                    return redirect("pharmacy:cart")

            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.subtotal
            order.delivery_fee = cart.delivery_fee
            order.total = cart.total
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    medicine=item.medicine,
                    medicine_name=item.medicine.name,
                    unit_price=item.medicine.price,
                    quantity=item.quantity,
                )
                item.medicine.stock -= item.quantity
                item.medicine.save(update_fields=["stock"])
            cart.clear()

        send_order_placed_email(order)
        messages.success(request, f"Order {order.order_id} placed successfully.")
        return redirect("pharmacy:order_detail", order_id=order.order_id)

    return render(request, "pharmacy/checkout.html", {"cart": cart, "form": form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "pharmacy/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), order_id=order_id, user=request.user
    )
    return render(request, "pharmacy/order_detail.html", {"order": order})
