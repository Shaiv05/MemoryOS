from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from chat.models import Conversation, Message, MessageSource
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
        self.assertIn("relevance_score", response.data["sources"][0])
        self.assertEqual(MessageSource.objects.count(), 1)
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

    def test_conversation_can_be_created_renamed_cleared_and_deleted(self):
        create_response = self.client.post(
            "/api/chat/conversations/",
            {"title": "Initial"},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        conversation_id = create_response.data["id"]

        rename_response = self.client.patch(
            f"/api/chat/conversations/{conversation_id}/",
            {"title": "Renamed"},
            format="json",
        )
        self.assertEqual(rename_response.status_code, 200)
        self.assertEqual(rename_response.data["title"], "Renamed")

        conversation = Conversation.objects.get(pk=conversation_id)
        Message.objects.create(conversation=conversation, role="user", content="Hello")
        clear_response = self.client.post(f"/api/chat/conversations/{conversation_id}/clear/")
        self.assertEqual(clear_response.status_code, 200)
        self.assertEqual(clear_response.data["messages"], [])

        delete_response = self.client.delete(f"/api/chat/conversations/{conversation_id}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Conversation.objects.filter(pk=conversation_id).exists())

    @patch("documents.services.retrieval.embed_query", return_value=[0.1] * 384)
    def test_chat_history_preserves_citations(self, _mock_embed):
        document = Document.objects.create(
            owner=self.user,
            title="Citation Notes",
            file_type="note",
            raw_text="Citations are persisted.",
        )
        DocumentChunk.objects.create(
            document=document,
            chunk_index=0,
            content="Citations are persisted.",
            embedding=[0.1] * 384,
            metadata={"page_number": 3},
        )
        chat_response = self.client.post(
            "/api/chat/message/",
            {"message": "What is persisted?"},
            format="json",
        )
        detail_response = self.client.get(
            f"/api/chat/conversations/{chat_response.data['conversation_id']}/"
        )

        self.assertEqual(detail_response.status_code, 200)
        assistant_message = detail_response.data["messages"][1]
        self.assertEqual(assistant_message["sources"][0]["page_number"], 3)
        self.assertEqual(assistant_message["sources"][0]["document_title"], "Citation Notes")
