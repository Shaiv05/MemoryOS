from django.conf import settings
from django.db import models

try:
    from pgvector.django import HnswIndex, VectorField
except ImportError:
    VectorField = None
    HnswIndex = None

_USING_POSTGRES = "postgres" in settings.DATABASES.get("default", {}).get("ENGINE", "")




class Document(models.Model):
    PROCESSING_PENDING = "pending"  # kept for legacy/compatibility
    PROCESSING_QUEUED = "queued"
    PROCESSING_PROCESSING = "processing"
    PROCESSING_COMPLETED = "completed"
    PROCESSING_FAILED = "failed"

    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("txt", "Text"),
        ("docx", "DOCX"),
        ("md", "Markdown"),
        ("image", "Image"),
        ("link", "Link"),
        ("note", "Note"),
    ]

    PROCESSING_STATUS_CHOICES = [
        (PROCESSING_QUEUED, "Queued"),
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
        default=PROCESSING_QUEUED,
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

    file_size = models.IntegerField(
        blank=True,
        null=True,
    )

    page_count = models.IntegerField(
        blank=True,
        null=True,
    )

    processing_started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    processing_completed_at = models.DateTimeField(
        blank=True,
        null=True,
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


class DocumentChunkManager(models.Manager):
    def create(self, **kwargs):
        if "content" in kwargs and "text" not in kwargs:
            kwargs["text"] = kwargs.pop("content")
        return super().create(**kwargs)


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    chunk_index = models.IntegerField()

    text = models.TextField()

    token_count = models.IntegerField(default=0)

    char_count = models.IntegerField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    if _USING_POSTGRES and VectorField is not None:
        embedding = VectorField(
            dimensions=384,
            null=True,
            blank=True,
        )
    else:
        embedding = models.JSONField(
            null=True,
            blank=True,
        )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = DocumentChunkManager()

    @property
    def content(self) -> str:
        return self.text

    @content.setter
    def content(self, value: str):
        self.text = value

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
        ]
        if _USING_POSTGRES and HnswIndex is not None:
            indexes.append(
                HnswIndex(
                    name="doc_chunk_embedding_hnsw",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                )
            )
