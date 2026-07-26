from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import MemoryEntry


class MemoryApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="ada",
            email="ada@example.com",
            password="strong-password-123",
        )
        self.other_user = user_model.objects.create_user(
            username="grace",
            email="grace@example.com",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)

    def test_create_memory_entry(self):
        response = self.client.post(
            "/api/memory/",
            {
                "title": "Writing preference",
                "content": "Prefers concise technical summaries.",
                "category": "preference",
                "tags": ["Writing", " concise "],
                "is_pinned": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["category"], "preference")
        self.assertEqual(response.data["tags"], ["writing", "concise"])
        self.assertTrue(response.data["is_pinned"])

    def test_list_searches_only_owned_memories(self):
        MemoryEntry.objects.create(
            owner=self.user,
            title="Owned memory",
            content="Postgres facts",
            category="fact",
        )
        MemoryEntry.objects.create(
            owner=self.other_user,
            title="Other memory",
            content="Postgres private",
            category="fact",
        )

        response = self.client.get("/api/memory/", {"q": "Postgres"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Owned memory")

    def test_user_cannot_update_another_users_memory(self):
        memory = MemoryEntry.objects.create(
            owner=self.other_user,
            title="Private",
            content="Secret",
            category="note",
        )

        response = self.client.patch(
            f"/api/memory/{memory.id}/",
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
