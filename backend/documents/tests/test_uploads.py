from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from documents.serializers import DocumentSerializer


class DocumentUploadSerializerTests(SimpleTestCase):
    def test_note_upload_is_valid_without_file(self):
        serializer = DocumentSerializer(
            data={
                "title": "Meeting notes",
                "file_type": "note",
                "raw_text": "A short note for the demo.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_pdf_upload_is_valid_with_uploaded_file(self):
        uploaded_file = SimpleUploadedFile(
            "demo.pdf",
            b"%PDF-1.4\n% demo",
            content_type="application/pdf",
        )
        serializer = DocumentSerializer(
            data={
                "title": "Demo PDF",
                "file_type": "pdf",
                "file": uploaded_file,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
