from django.db import transaction
from django.utils import timezone

from documents.models import Document, DocumentChunk

from .chunking import chunk_text, replace_document_chunks
from .embeddings import embed_chunks
from .extraction import extract_document_text


def process_document(document):
    document.processing_status = Document.PROCESSING_PROCESSING
    document.processing_error = ""
    document.save(update_fields=["processing_status", "processing_error", "updated_at"])

    try:
        raw_text = extract_document_text(document)
        chunks = chunk_text(raw_text)
        if not chunks:
            raise ValueError("Document text did not produce any chunks.")

        with transaction.atomic():
            document.raw_text = raw_text
            document.extracted_at = timezone.now()
            document.source_checksum = ""
            document.save(update_fields=["raw_text", "extracted_at", "source_checksum", "updated_at"])
            replace_document_chunks(document, chunks)

        chunk_queryset = DocumentChunk.objects.filter(document=document).order_by("chunk_index")
        embed_chunks(chunk_queryset)

        document.processing_status = Document.PROCESSING_COMPLETED
        document.processing_error = ""
        document.save(update_fields=["processing_status", "processing_error", "updated_at"])
    except Exception as exc:
        document.processing_status = Document.PROCESSING_FAILED
        document.processing_error = str(exc)[:2000]
        document.save(update_fields=["processing_status", "processing_error", "updated_at"])

    return document
