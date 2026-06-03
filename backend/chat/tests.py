from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from chat.models import Conversation, Message
from documents.models import Document, DocumentChunk


class ChatApiTests(APITestCase):
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

    @patch("documents.services.retrieval.embed_query", return_value=[0.1] * 384)
    def test_chat_creates_history_and_sources(self, _mock_embed):
        document = Document.objects.create(
            owner=self.user,
            title="Search Notes",
            file_type="note",
            raw_text="Semantic retrieval finds relevant chunks.",
        )
        chunk = DocumentChunk.objects.create(
            document=document,
            chunk_index=0,
            content="Semantic retrieval finds relevant chunks.",
            embedding=[0.1] * 384,
        )

        response = self.client.post(
            "/api/chat/message/",
            {"message": "What does semantic retrieval find?"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sources"][0]["chunk_id"], chunk.id)
        self.assertIn("answer", response.data)
        self.assertEqual(Conversation.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(Message.objects.count(), 2)

    @patch("documents.services.retrieval.embed_query", return_value=[0.1] * 384)
    def test_chat_retrieval_only_uses_owned_documents(self, _mock_embed):
        owned_doc = Document.objects.create(
            owner=self.user,
            title="Owned",
            file_type="note",
            raw_text="Owned document content.",
        )
        DocumentChunk.objects.create(
            document=owned_doc,
            chunk_index=0,
            content="Owned document content.",
            embedding=[0.1] * 384,
        )
        other_doc = Document.objects.create(
            owner=self.other_user,
            title="Other",
            file_type="note",
            raw_text="Other user secret content.",
        )
        DocumentChunk.objects.create(
            document=other_doc,
            chunk_index=0,
            content="Other user secret content.",
            embedding=[0.1] * 384,
        )

        response = self.client.post(
            "/api/chat/message/",
            {"message": "Find content"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["sources"]), 1)
        self.assertEqual(response.data["sources"][0]["document_title"], "Owned")

    def test_user_cannot_load_another_users_conversation(self):
        conversation = Conversation.objects.create(
            owner=self.other_user,
            title="Private chat",
        )

        response = self.client.get(f"/api/chat/conversations/{conversation.id}/")

        self.assertEqual(response.status_code, 404)
