import hashlib
import logging
from django.db import transaction
from django.utils import timezone

from documents.models import Document, DocumentChunk
from .chunker import chunk_text
from .chunking import replace_document_chunks
from .embeddings import embed_chunks
from .extraction import extract_document_text

logger = logging.getLogger(__name__)

try:
    from graph.services import process_document_for_graph
except Exception:
    process_document_for_graph = None


def compute_checksum(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def process_document(document: Document) -> Document:
    """
    Processes an uploaded document:
      1. Extract text and populate basic metadata (file size, page count).
      2. Status transition to 'processing'.
      3. Create intelligent chunks using sentence-boundary chunker.
      4. Compute vector embeddings.
      5. Extract Knowledge Graph entities.
      6. Status transition to 'completed' or 'failed'.
    """
    document.processing_status = Document.PROCESSING_PROCESSING
    document.processing_started_at = timezone.now()
    document.processing_error = ""

    if document.file:
        try:
            document.file_size = document.file.size
        except Exception:
            pass

    if document.file_type == "pdf" and document.file:
        try:
            from pypdf import PdfReader
            reader = PdfReader(document.file.path)
            document.page_count = len(reader.pages)
        except Exception:
            pass

    document.save(update_fields=[
        "processing_status",
        "processing_started_at",
        "processing_error",
        "file_size",
        "page_count",
        "updated_at",
    ])

    try:
        raw_text = extract_document_text(document)
        checksum = compute_checksum(raw_text)

        chunks = chunk_text(raw_text)
        if not chunks:
            raise ValueError("Document text did not produce any valid chunks.")

        with transaction.atomic():
            document.raw_text = raw_text
            document.extracted_at = timezone.now()
            document.source_checksum = checksum
            document.save(update_fields=["raw_text", "extracted_at", "source_checksum", "updated_at"])

            replace_document_chunks(document, chunks)

        chunk_queryset = DocumentChunk.objects.filter(document=document).order_by("chunk_index")
        try:
            embed_chunks(chunk_queryset)
        except Exception as embed_err:
            logger.warning("Embedding generation failed for document %s: %s", document.id, embed_err)

        if process_document_for_graph is not None:
            try:
                process_document_for_graph(document.owner, document)
            except Exception as graph_err:
                logger.warning("Graph extraction failed for document %s: %s", document.id, graph_err)

        document.processing_status = Document.PROCESSING_COMPLETED
        document.processing_completed_at = timezone.now()
        document.processing_error = ""
        document.save(update_fields=["processing_status", "processing_completed_at", "processing_error", "updated_at"])

    except Exception as exc:
        document.processing_status = Document.PROCESSING_FAILED
        document.processing_completed_at = timezone.now()
        document.processing_error = str(exc)[:2000]
        document.save(update_fields=["processing_status", "processing_completed_at", "processing_error", "updated_at"])

    return document
