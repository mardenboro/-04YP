from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Brand, Instrument
from apps.clients.models import Client
from apps.orders.models import Order


class ReportsApiTests(APITestCase):
    """Модуль 5: отчёты (интеграция с заказами и каталогом)."""

    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="Secret123!")
        self.client.force_authenticate(self.user)
        buyer = Client.objects.create(full_name="Смирнова Анна", phone="+79001112233")
        brand = Brand.objects.create(name="Fender")
        guitar = Instrument.objects.create(
            brand=brand, model="Player Stratocaster", category=Instrument.Category.GUITAR,
            year=2023, price=119990,
        )
        Instrument.objects.create(
            brand=brand, model="Player Telecaster", category=Instrument.Category.GUITAR,
            year=2023, price=114990,
        )
        self.order = Order.objects.create(
            client=buyer, instrument=guitar, manager=self.user,
            order_type=Order.OrderType.PURCHASE, total_amount=119990,
        )

    def test_kpi_updates_after_completion(self):
        before = self.client.get("/api/reports/kpi/").data
        self.assertEqual(before["sales_count"], 0)
        self.order.complete()
        after = self.client.get("/api/reports/kpi/").data
        self.assertEqual(after["sales_count"], 1)
        self.assertEqual(after["revenue"], 119990.0)
        self.assertEqual(after["in_stock"], 1)

    def test_revenue_and_top_models(self):
        self.order.complete()
        revenue = self.client.get("/api/reports/revenue/").data
        self.assertEqual(len(revenue), 1)
        top = self.client.get("/api/reports/top-models/").data
        self.assertEqual(top[0]["model"], "Player Stratocaster")

    def test_manager_load_and_stock(self):
        load = self.client.get("/api/reports/manager-load/").data
        self.assertEqual(load[0]["orders"], 1)
        stock = {r["status"]: r["count"] for r in self.client.get("/api/reports/stock/").data}
        self.assertEqual(stock, {"available": 1, "reserved": 1})

    def test_reports_require_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/reports/kpi/").status_code, 401)
