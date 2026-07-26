from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

from documents.models import Document, DocumentChunk


def fake_embed_chunks(chunks):
    chunk_list = list(chunks)
    for chunk in chunk_list:
        chunk.embedding = [0.0] * 384
    DocumentChunk.objects.bulk_update(chunk_list, ["embedding"])
    return chunk_list


class DocumentApiTests(APITestCase):
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

    @patch("documents.services.processing.embed_chunks", side_effect=fake_embed_chunks)
    def test_create_note_processes_document(self, _mock_embed):
        response = self.client.post(
            "/api/documents/",
            {
                "title": "Retrieval note",
                "file_type": "note",
                "raw_text": "Chunk this useful note about semantic search." * 20,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["processing_status"], Document.PROCESSING_COMPLETED)
        self.assertGreater(response.data["chunk_count"], 0)

    def test_note_requires_raw_text(self):
        response = self.client.post(
            "/api/documents/",
            {"title": "Empty note", "file_type": "note", "raw_text": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("raw_text", response.data)

    def test_user_cannot_access_another_users_document(self):
        document = Document.objects.create(
            owner=self.other_user,
            title="Private",
            file_type="note",
            raw_text="private text",
        )

        response = self.client.get(f"/api/documents/{document.id}/")

        self.assertEqual(response.status_code, 404)
