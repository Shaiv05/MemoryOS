from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from documents.models import Document, DocumentChunk


class SemanticSearchApiTests(APITestCase):
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

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.post(
            "/api/search/",
            {"query": "search query"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    @patch("documents.services.retrieval.embed_query", return_value=[0.1] * 384)
    def test_authenticated_search_returns_chunks_and_similarity(self, mock_embed):
        self.client.force_authenticate(self.user)
        doc = Document.objects.create(
            owner=self.user,
            title="Ada Notes",
            file_type="note",
            raw_text="Hello world test",
        )
        chunk1 = DocumentChunk.objects.create(
            document=doc,
            chunk_index=0,
            content="Hello world test",
            embedding=[0.1] * 384
        )

        response = self.client.post(
            "/api/search/",
            {"query": "test query", "limit": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["chunk_id"], chunk1.id)
        self.assertEqual(response.data[0]["document_title"], "Ada Notes")
        self.assertIn("similarity_score", response.data[0])
        # CosineDistance of same vector [0.1]*384 is 0.0, similarity is 1.0
        self.assertAlmostEqual(response.data[0]["similarity_score"], 1.0, places=4)

    @patch("documents.services.retrieval.embed_query", return_value=[0.1] * 384)
    def test_search_only_returns_own_documents(self, mock_embed):
        self.client.force_authenticate(self.user)

        # User 1's doc
        doc1 = Document.objects.create(
            owner=self.user,
            title="Ada Notes",
            file_type="note",
            raw_text="Hello world test",
        )
        DocumentChunk.objects.create(
            document=doc1,
            chunk_index=0,
            content="Hello world test",
            embedding=[0.1] * 384
        )

        # User 2's doc
        doc2 = Document.objects.create(
            owner=self.other_user,
            title="Grace Notes",
            file_type="note",
            raw_text="Secret document contents",
        )
        DocumentChunk.objects.create(
            document=doc2,
            chunk_index=0,
            content="Secret document contents",
            embedding=[0.1] * 384
        )

        response = self.client.post(
            "/api/search/",
            {"query": "test query"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["document_title"], "Ada Notes")
