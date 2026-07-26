from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def test_register_login_me_and_password_change(self):
        # 1. Register
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

        # 2. Login
        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "ada", "password": "strong-password-123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # 3. Me endpoint GET
        me_response = self.client.get("/api/auth/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["username"], "ada")
        self.assertEqual(me_response.data["email"], "ada@example.com")

        # 4. Profile PATCH
        patch_response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "Ada", "last_name": "Lovelace"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data["first_name"], "Ada")

        # 5. Change password
        pwd_response = self.client.post(
            "/api/auth/change-password/",
            {
                "old_password": "strong-password-123",
                "new_password": "new-strong-password-456",
            },
            format="json",
        )
        self.assertEqual(pwd_response.status_code, 200)

        # 6. Logout / Blacklist token
        logout_response = self.client.post(
            "/api/auth/logout/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(logout_response.status_code, 200)
