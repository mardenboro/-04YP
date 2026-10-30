from rest_framework.test import APITestCase

from .models import User


class AuthApiTests(APITestCase):
    """Модуль 1: регистрация, вход по JWT, профиль."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="ivanov", password="Secret123!", position=User.Position.MANAGER,
        )

    def test_register_returns_tokens(self):
        response = self.client.post("/api/auth/register/", {
            "username": "petrov", "email": "petrov@kamerton.ru",
            "password": "Secret123!", "password2": "Secret123!",
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertTrue(User.objects.filter(username="petrov").exists())

    def test_register_passwords_mismatch(self):
        response = self.client.post("/api/auth/register/", {
            "username": "petrov", "password": "Secret123!", "password2": "Other123!",
        })
        self.assertEqual(response.status_code, 400)

    def test_login_and_me(self):
        response = self.client.post("/api/auth/login/", {"username": "ivanov", "password": "Secret123!"})
        self.assertEqual(response.status_code, 200)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["username"], "ivanov")

    def test_login_wrong_password(self):
        response = self.client.post("/api/auth/login/", {"username": "ivanov", "password": "wrong"})
        self.assertEqual(response.status_code, 400)

    def test_me_without_token(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
