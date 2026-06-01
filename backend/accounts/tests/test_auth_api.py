from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def test_register_login_and_me(self):
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "username": "ada",
                "email": "ada@example.com",
                "password": "strong-password-123",
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertTrue(get_user_model().objects.filter(username="ada").exists())

        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "ada", "password": "strong-password-123"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )
        me_response = self.client.get("/api/auth/me/")

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["username"], "ada")
