"""
Management command to reprocess all existing documents in MemoryOS using the
new PyMuPDF semantic chunking RAG pipeline.

Usage:
  python manage.py reprocess_documents
  python manage.py reprocess_documents --doc-id=5
"""

import logging
from django.core.management.base import BaseCommand
from documents.models import Document
from documents.services.document_processor import process_document

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reprocess existing documents with PyMuPDF semantic chunking pipeline."

    def add_arguments(self, parser):
        parser.add_argument(
            "--doc-id",
            type=int,
            help="Reprocess a specific document ID only",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reprocess even if document status is COMPLETED",
        )

    def handle(self, *args, **options):
        doc_id = options.get("doc_id")
        force = options.get("force")

        if doc_id:
            qs = Document.objects.filter(id=doc_id)
        elif force:
            qs = Document.objects.all()
        else:
            qs = Document.objects.exclude(processing_status=Document.PROCESSING_COMPLETED)

        total = qs.count()
        self.stdout.write(self.style.NOTICE(f"Found {total} document(s) to reprocess."))

        success = 0
        failed = 0

        for doc in qs:
            self.stdout.write(f"Reprocessing document {doc.id}: '{doc.title}'...")
            try:
                process_document(doc)
                doc.refresh_from_db()
                if doc.processing_status == Document.PROCESSING_COMPLETED:
                    chunk_cnt = doc.chunks.count()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  SUCCESS: Document {doc.id} produced {chunk_cnt} chunks."
                        )
                    )
                    success += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  FAILED: Document {doc.id} error: {doc.processing_error}"
                        )
                    )
                    failed += 1
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR processing document {doc.id}: {exc}")
                )
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nReprocessing completed: {success} succeeded, {failed} failed out of {total} total."
            )
        )
