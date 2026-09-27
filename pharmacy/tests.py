"""Patient-facing pharmacy flows: browse, cart, checkout, orders."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Cart, CartItem, Category, Medicine, Order

User = get_user_model()


class PharmacyFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="patient", email="patient@example.com", password="patient12345"
        )
        self.category = Category.objects.create(name="Pain Relief")
        self.medicine = Medicine.objects.create(
            name="Paracetamol 500mg",
            category=self.category,
            brand="MediCare",
            price=Decimal("20.00"),
            stock=10,
        )
        self.out_of_stock = Medicine.objects.create(
            name="Antihistamine", category=self.category, price=Decimal("12.00"), stock=0
        )

    def login(self):
        self.client.login(username="patient", password="patient12345")

    def test_medicine_list_is_public_and_searchable(self):
        response = self.client.get(reverse("pharmacy:medicine_list"), {"q": "Paracetamol"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paracetamol 500mg")

    def test_add_to_cart_and_totals(self):
        self.login()
        self.client.post(
            reverse("pharmacy:add_to_cart", args=[self.medicine.pk]), {"quantity": 3}
        )
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items_count, 3)
        self.assertEqual(cart.subtotal, Decimal("60.00"))

    def test_cannot_add_more_than_stock(self):
        self.login()
        self.client.post(
            reverse("pharmacy:add_to_cart", args=[self.medicine.pk]), {"quantity": 99}
        )
        cart = Cart.objects.filter(user=self.user).first()
        self.assertTrue(cart is None or cart.items_count <= self.medicine.stock)

    def test_out_of_stock_cannot_be_added(self):
        self.login()
        self.client.post(
            reverse("pharmacy:add_to_cart", args=[self.out_of_stock.pk]), {"quantity": 1}
        )
        self.assertFalse(
            CartItem.objects.filter(medicine=self.out_of_stock).exists()
        )

    def test_checkout_creates_order_decrements_stock_and_emails(self):
        self.login()
        self.client.post(
            reverse("pharmacy:add_to_cart", args=[self.medicine.pk]), {"quantity": 2}
        )
        mail.outbox.clear()
        response = self.client.post(
            reverse("pharmacy:checkout"),
            {
                "full_name": "Sam Taylor",
                "email": "patient@example.com",
                "phone": "+1 555 0100",
                "address": "42 Maple Street",
                "city": "Springfield",
                "postal_code": "12345",
                "payment_method": "cod",
                "notes": "",
            },
        )
        order = Order.objects.get()
        self.assertRedirects(
            response, reverse("pharmacy:order_detail", args=[order.order_id])
        )
        self.assertTrue(order.order_id.startswith("HC-"))
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.items.count(), 1)
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 8)
        self.assertEqual(Cart.objects.get(user=self.user).items_count, 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_orders_are_private(self):
        self.login()
        self.client.post(
            reverse("pharmacy:add_to_cart", args=[self.medicine.pk]), {"quantity": 1}
        )
        self.client.post(
            reverse("pharmacy:checkout"),
            {
                "full_name": "Sam Taylor",
                "email": "patient@example.com",
                "phone": "+1 555 0100",
                "address": "42 Maple Street",
                "city": "Springfield",
                "payment_method": "cod",
            },
        )
        order = Order.objects.get()
        self.client.logout()
        other = User.objects.create_user(username="other", password="other12345")
        self.client.force_login(other)
        response = self.client.get(
            reverse("pharmacy:order_detail", args=[order.order_id])
        )
        self.assertEqual(response.status_code, 404)
