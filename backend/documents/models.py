from django.conf import settings
from django.db import models
from pgvector.django import HnswIndex, VectorField


class Document(models.Model):
    PROCESSING_PENDING = "pending"
    PROCESSING_PROCESSING = "processing"
    PROCESSING_COMPLETED = "completed"
    PROCESSING_FAILED = "failed"

    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("txt", "Text"),
        ("docx", "DOCX"),
        ("link", "Link"),
        ("note", "Note"),
    ]

    PROCESSING_STATUS_CHOICES = [
        (PROCESSING_PENDING, "Pending"),
        (PROCESSING_PROCESSING, "Processing"),
        (PROCESSING_COMPLETED, "Completed"),
        (PROCESSING_FAILED, "Failed"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="documents/",
        blank=True,
        null=True,
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
    )

    source_url = models.URLField(
        blank=True,
        null=True,
    )

    raw_text = models.TextField(
        blank=True,
        default="",
    )

    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default=PROCESSING_PENDING,
    )

    processing_error = models.TextField(
        blank=True,
        default="",
    )

    extracted_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    source_checksum = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["owner", "processing_status"], name="doc_owner_status_idx"),
            models.Index(fields=["owner", "-created_at"], name="doc_owner_created_idx"),
        ]


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    chunk_index = models.IntegerField()

    content = models.TextField()

    embedding = VectorField(
        dimensions=384,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk_index",
            ),
        ]
        indexes = [
            models.Index(fields=["document", "chunk_index"], name="chunk_document_order_idx"),
            HnswIndex(
                name="doc_chunk_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]
