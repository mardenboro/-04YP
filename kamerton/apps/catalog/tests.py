from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Brand, Instrument


class CatalogApiTests(APITestCase):
    """Модуль 2: каталог инструментов."""

    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="Secret123!")
        self.client.force_authenticate(self.user)
        self.yamaha = Brand.objects.create(name="Yamaha", country="Япония")
        self.fender = Brand.objects.create(name="Fender", country="США")
        Instrument.objects.create(
            brand=self.yamaha, model="P-125", category=Instrument.Category.KEYS,
            year=2024, price=69990,
        )
        self.strat = Instrument.objects.create(
            brand=self.fender, model="Player Stratocaster", category=Instrument.Category.GUITAR,
            year=2023, price=119990, serial_number="MX23012345",
        )

    def test_list_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/instruments/").status_code, 401)

    def test_list(self):
        response = self.client.get("/api/instruments/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_category(self):
        response = self.client.get("/api/instruments/", {"category": "guitar"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["brand_name"], "Fender")

    def test_search_by_brand(self):
        response = self.client.get("/api/instruments/", {"search": "yamaha"})
        self.assertEqual(response.data["count"], 1)

    def test_create(self):
        response = self.client.post("/api/instruments/", {
            "brand": self.yamaha.pk, "model": "F310", "category": "guitar",
            "year": 2025, "price": "12990.00",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "available")

    def test_change_status(self):
        response = self.client.patch(f"/api/instruments/{self.strat.pk}/status/", {"status": "sold"})
        self.assertEqual(response.status_code, 200)
        self.strat.refresh_from_db()
        self.assertEqual(self.strat.status, Instrument.Status.SOLD)

    def test_brand_name_unique(self):
        response = self.client.post("/api/brands/", {"name": "Yamaha"})
        self.assertEqual(response.status_code, 400)
