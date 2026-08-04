from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from documents.models import Document, DocumentChunk
from documents.services.chunker import chunk_text
from documents.services.processing import process_document
from documents.services.retrieval import search_document_chunks
from documents.services.validation import validate_chunks


def fake_embed_chunks(chunks):
    chunk_list = list(chunks)
    for chunk in chunk_list:
        chunk.embedding = [0.01 * (i + 1) for i in range(384)]
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
        text = "# Chapter 1: Data Structures\n\n" + " ".join(["knowledge"] * 300)

        first = chunk_text(text, chunk_size=120, overlap=20)
        second = chunk_text(text, chunk_size=120, overlap=20)

        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)

    def test_semantic_chunking_preserves_headings(self):
        sample_doc = (
            "# Chapter 1: Introduction to Data Structures and Algorithmic Analysis\n\n"
            "A data structure is a specialized format for organizing, processing, retrieving and storing data in computer memory efficiently. "
            "Data structures provide a structured means of managing large amounts of data efficiently for uses such as large databases and internet indexing services.\n\n"
            "## Primary Classifications of Data Structures\n\n"
            "1. Linear Data Structures: Elements are arranged sequentially or linearly, where each element is attached to its previous and next adjacent elements. Examples include Arrays, Linked Lists, Stacks, and Queues.\n"
            "2. Non-Linear Data Structures: Elements are not arranged sequentially or linearly. Examples include Trees, Graphs, and Hash Tables.\n\n"
            "### Detailed Definition of Array Data Structure\n\n"
            "An array is a linear data structure containing a collection of elements, each identified by at least one array index or key. "
            "It is stored in contiguous memory locations so that the position of each element can be computed directly by an index offset."
        )

        chunks = chunk_text(sample_doc, chunk_size=500, overlap=50)
        self.assertGreater(len(chunks), 0)

        # Check metadata in chunks
        has_heading = any(
            c.get("metadata", {}).get("heading") != ""
            for c in chunks
        )
        self.assertTrue(has_heading)

        # Check validation
        report = validate_chunks(chunks)
        self.assertTrue(report["passed"], f"Validation failed: {report['issues']}")

    @patch("documents.services.document_processor.embed_chunks", side_effect=fake_embed_chunks)
    def test_process_note_creates_chunks_and_marks_completed(self, _mock_embed):
        document = Document.objects.create(
            owner=self.user,
            title="Data Structures Chapter 1",
            file_type="note",
            raw_text=(
                "# Chapter 1: Introduction to Data Structures\n\n"
                "A data structure is a specialized format for organizing, processing, retrieving and storing data in computer memory. "
                "Data structures make it easy for users to access and work with the data they need in an appropriate way.\n\n"
                "## Key Concepts and Theoretical Foundations\n\n"
                "Data structures are the foundational building blocks of efficient software algorithms and system design."
            ),
        )

        process_document(document)
        document.refresh_from_db()

        self.assertEqual(document.processing_status, Document.PROCESSING_COMPLETED)
        self.assertEqual(document.processing_error, "")
        self.assertGreater(document.chunks.count(), 0)
        self.assertIsNotNone(document.extracted_at)

        # Test retrieval finding exact definition chunk
        results = search_document_chunks(self.user, "What is Data Structure?")
        self.assertGreater(len(results), 0)
        self.assertIn("data structure is a specialized format", results[0].text.lower())
