from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Client


class ClientApiTests(APITestCase):
    """Модуль 3: клиенты."""

    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="Secret123!")
        self.client.force_authenticate(self.user)
        Client.objects.create(full_name="Смирнова Анна", phone="+79001112233", manager=self.user)

    def test_create(self):
        response = self.client.post("/api/clients/", {"full_name": "Козлов Пётр", "phone": "+79004445566"})
        self.assertEqual(response.status_code, 201)

    def test_phone_unique(self):
        response = self.client.post("/api/clients/", {"full_name": "Другой", "phone": "+79001112233"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_search(self):
        response = self.client.get("/api/clients/", {"search": "Смирнова"})
        self.assertEqual(response.data["count"], 1)
