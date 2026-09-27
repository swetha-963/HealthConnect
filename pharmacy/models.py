import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="medicines"
    )
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    prescription_required = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="medicines/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "medicine"
            slug = base
            counter = 2
            while Medicine.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("pharmacy:medicine_detail", args=[self.slug])

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def is_low_stock(self) -> bool:
        return 0 < self.stock <= self.low_stock_threshold

    @property
    def stock_label(self) -> str:
        if not self.in_stock:
            return "Out of stock"
        if self.is_low_stock:
            return f"Only {self.stock} left"
        return "In stock"

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self) -> Decimal:
        return sum((item.total_price for item in self.items.all()), Decimal("0.00"))

    @property
    def delivery_fee(self) -> Decimal:
        threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
        fee = Decimal(str(settings.DELIVERY_FEE))
        if self.subtotal == 0 or self.subtotal >= threshold:
            return Decimal("0.00")
        return fee

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.delivery_fee

    def clear(self):
        self.items.all().delete()

    def __str__(self) -> str:
        return f"Cart of {self.user.display_name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "medicine")
        ordering = ["added_at"]

    @property
    def total_price(self) -> Decimal:
        return self.medicine.price * self.quantity

    def __str__(self) -> str:
        return f"{self.medicine.name} x{self.quantity}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class Payment(models.TextChoices):
        COD = "cod", "Cash on delivery"
        CARD = "card", "Card on delivery"

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=10, choices=Payment.choices, default=Payment.COD
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"HC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def status_class(self) -> str:
        return {
            self.Status.PENDING: "badge-warning",
            self.Status.CONFIRMED: "badge-info",
            self.Status.PACKED: "badge-info",
            self.Status.SHIPPED: "badge-info",
            self.Status.DELIVERED: "badge-success",
            self.Status.CANCELLED: "badge-danger",
        }[self.Status(self.status)]

    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items.all())

    def __str__(self) -> str:
        return f"{self.order_id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True)
    medicine_name = models.CharField(max_length=140)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return f"{self.medicine_name} x{self.quantity}"
