from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from documents.models import Document, DocumentChunk
from documents.services.chunking import chunk_text
from documents.services.processing import process_document


def fake_embed_chunks(chunks):
    chunk_list = list(chunks)
    for chunk in chunk_list:
        chunk.embedding = [0.0] * 384
    DocumentChunk.objects.bulk_update(chunk_list, ["embedding"])
    return chunk_list


class DocumentProcessingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ada",
            email="ada@example.com",
            password="strong-password-123",
        )

    def test_chunk_text_is_deterministic(self):
        text = " ".join(["knowledge"] * 300)

        first = chunk_text(text, chunk_size=120, overlap=20)
        second = chunk_text(text, chunk_size=120, overlap=20)

        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)

    @patch("documents.services.processing.embed_chunks", side_effect=fake_embed_chunks)
    def test_process_note_creates_chunks_and_marks_completed(self, _mock_embed):
        document = Document.objects.create(
            owner=self.user,
            title="PKM note",
            file_type="note",
            raw_text="This is a useful note about retrieval and memory." * 20,
        )

        process_document(document)
        document.refresh_from_db()

        self.assertEqual(document.processing_status, Document.PROCESSING_COMPLETED)
        self.assertEqual(document.processing_error, "")
        self.assertGreater(document.chunks.count(), 0)
        self.assertIsNotNone(document.extracted_at)
