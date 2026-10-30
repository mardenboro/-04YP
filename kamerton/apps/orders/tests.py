from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Brand, Instrument
from apps.clients.models import Client

from .models import Order


class OrderCascadeTests(APITestCase):
    """Модуль 4: заказы и каскадная смена статуса инструмента."""

    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="Secret123!")
        self.client.force_authenticate(self.user)
        self.buyer = Client.objects.create(full_name="Смирнова Анна", phone="+79001112233")
        brand = Brand.objects.create(name="Yamaha")
        self.piano = Instrument.objects.create(
            brand=brand, model="P-125", category=Instrument.Category.KEYS, year=2024, price=69990,
        )

    def make_order(self, order_type):
        return Order.objects.create(
            client=self.buyer, instrument=self.piano, manager=self.user,
            order_type=order_type, total_amount=69990,
        )

    def test_purchase_reserves_then_sells(self):
        order = self.make_order(Order.OrderType.PURCHASE)
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.RESERVED)
        order.complete()
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.SOLD)
        self.assertIsNotNone(order.completed_at)

    def test_rental_and_return(self):
        order = self.make_order(Order.OrderType.RENTAL)
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.RENTED)
        order.complete()
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.AVAILABLE)

    def test_cancel_returns_to_stock(self):
        order = self.make_order(Order.OrderType.PURCHASE)
        order.cancel()
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.AVAILABLE)
        self.assertEqual(order.status, Order.Status.CANCELLED)

    def test_repair_does_not_change_status(self):
        self.make_order(Order.OrderType.REPAIR)
        self.piano.refresh_from_db()
        self.assertEqual(self.piano.status, Instrument.Status.AVAILABLE)

    def test_api_create_sets_manager(self):
        response = self.client.post("/api/orders/", {
            "client": self.buyer.pk, "instrument": self.piano.pk,
            "order_type": "purchase", "total_amount": "69990.00",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["manager"], self.user.pk)

    def test_api_cannot_buy_reserved(self):
        self.make_order(Order.OrderType.PURCHASE)
        response = self.client.post("/api/orders/", {
            "client": self.buyer.pk, "instrument": self.piano.pk, "order_type": "purchase",
        })
        self.assertEqual(response.status_code, 400)

    def test_api_complete_and_repeat(self):
        order = self.make_order(Order.OrderType.PURCHASE)
        response = self.client.post(f"/api/orders/{order.pk}/complete/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "completed")
        again = self.client.post(f"/api/orders/{order.pk}/complete/")
        self.assertEqual(again.status_code, 400)
