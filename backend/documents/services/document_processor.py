"""
Document processing orchestrator.

Pipeline: Extract → Clean → Chunk → Validate → Embed → Graph
Includes structured logging with timing for every stage.
"""

import hashlib
import logging
import time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from documents.models import Document, DocumentChunk
from .chunker import chunk_text
from .chunking import replace_document_chunks
from .embeddings import embed_chunks
from .extraction import extract_document_text
from .validation import log_validation_report, validate_chunks

logger = logging.getLogger(__name__)

try:
    from graph.services import process_document_for_graph
except Exception:
    process_document_for_graph = None


def compute_checksum(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _timed(label: str):
    """Simple context manager that logs elapsed time."""

    class _Timer:
        def __init__(self):
            self.elapsed = 0.0

        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            self.elapsed = time.time() - self.start
            logger.info("  [%s] %.2fs", label, self.elapsed)

    return _Timer()


def process_document(document: Document) -> Document:
    """
    Full document processing pipeline:
      1. Extract text (PyMuPDF → pypdf fallback)
      2. Populate metadata (file size, page count)
      3. Create semantic chunks with rich metadata
      4. Validate chunks
      5. Generate vector embeddings
      6. Extract Knowledge Graph entities
      7. Transition status to completed / failed
    """
    total_start = time.time()
    document.processing_status = Document.PROCESSING_PROCESSING
    document.processing_started_at = timezone.now()
    document.processing_error = ""

    # --- File metadata ---
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

    document.save(
        update_fields=[
            "processing_status",
            "processing_started_at",
            "processing_error",
            "file_size",
            "page_count",
            "updated_at",
        ]
    )

    logger.info(
        "Processing document %d: '%s' (type=%s, size=%s)",
        document.id,
        document.title,
        document.file_type,
        document.file_size,
    )

    try:
        # ── Stage 1: Text Extraction ─────────────────────────────────────
        with _timed("Extraction") as t_extract:
            raw_text = extract_document_text(document)
            checksum = compute_checksum(raw_text)

        logger.info(
            "  Extracted %d chars (checksum=%s)",
            len(raw_text),
            checksum[:8],
        )

        # ── Stage 2: Semantic Chunking ───────────────────────────────────
        with _timed("Chunking") as t_chunk:
            chunks = chunk_text(raw_text)

        if not chunks:
            raise ValueError("Document text did not produce any valid chunks.")

        logger.info("  Produced %d chunks", len(chunks))

        # ── Stage 3: Chunk Validation ────────────────────────────────────
        validation_enabled = getattr(settings, "RAG_VALIDATION_ENABLED", True)
        validation_report = None
        if validation_enabled:
            with _timed("Validation"):
                validation_report = validate_chunks(chunks)
                log_validation_report(validation_report, document.title)

            # Filter out empty chunks
            original_count = len(chunks)
            chunks = [c for c in chunks if c.get("text", "").strip()]
            if len(chunks) < original_count:
                logger.info(
                    "  Filtered %d empty chunks → %d remaining",
                    original_count - len(chunks),
                    len(chunks),
                )

        if not chunks:
            raise ValueError("All chunks were empty after validation.")

        # ── Stage 4: Persist text and chunks ─────────────────────────────
        with _timed("DB Write") as t_db:
            with transaction.atomic():
                document.raw_text = raw_text
                document.extracted_at = timezone.now()
                document.source_checksum = checksum
                document.save(
                    update_fields=[
                        "raw_text",
                        "extracted_at",
                        "source_checksum",
                        "updated_at",
                    ]
                )
                replace_document_chunks(document, chunks)

        # ── Stage 5: Embedding Generation ────────────────────────────────
        chunk_queryset = DocumentChunk.objects.filter(document=document).order_by(
            "chunk_index"
        )
        with _timed("Embedding") as t_embed:
            try:
                embed_chunks(chunk_queryset)
            except Exception as embed_err:
                logger.error(
                    "Embedding generation failed for document %d: %s",
                    document.id,
                    embed_err,
                )
                # Don't fail the entire pipeline — chunks are still usable
                # for keyword search even without embeddings

        # ── Stage 6: Knowledge Graph ─────────────────────────────────────
        if process_document_for_graph is not None:
            with _timed("Graph") as t_graph:
                try:
                    process_document_for_graph(document.owner, document)
                except Exception as graph_err:
                    logger.warning(
                        "Graph extraction failed for document %d: %s",
                        document.id,
                        graph_err,
                    )

        # ── Stage 7: Mark completed ──────────────────────────────────────
        document.processing_status = Document.PROCESSING_COMPLETED
        document.processing_completed_at = timezone.now()
        document.processing_error = ""
        document.save(
            update_fields=[
                "processing_status",
                "processing_completed_at",
                "processing_error",
                "updated_at",
            ]
        )

        total_elapsed = time.time() - total_start
        final_chunk_count = DocumentChunk.objects.filter(document=document).count()
        embedded_count = DocumentChunk.objects.filter(
            document=document, embedding__isnull=False
        ).count()

        logger.info(
            "Document %d processed successfully in %.2fs: "
            "%d pages, %d chunks, %d embedded",
            document.id,
            total_elapsed,
            document.page_count or 0,
            final_chunk_count,
            embedded_count,
        )

    except Exception as exc:
        document.processing_status = Document.PROCESSING_FAILED
        document.processing_completed_at = timezone.now()
        document.processing_error = str(exc)[:2000]
        document.save(
            update_fields=[
                "processing_status",
                "processing_completed_at",
                "processing_error",
                "updated_at",
            ]
        )
        logger.error(
            "Document %d processing FAILED after %.2fs: %s",
            document.id,
            time.time() - total_start,
            exc,
            exc_info=True,
        )

    return document
