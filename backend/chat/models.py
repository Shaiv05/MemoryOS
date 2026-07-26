from django.conf import settings
from django.db import models

from documents.models import Document, DocumentChunk


class Conversation(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("system", "System"),
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    cited_chunks = models.ManyToManyField(DocumentChunk, blank=True, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:80]}"


class MessageSource(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="sources",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="message_sources",
    )
    document_chunk = models.ForeignKey(
        DocumentChunk,
        on_delete=models.CASCADE,
        related_name="message_sources",
    )
    page_number = models.IntegerField(blank=True, null=True)
    relevance_score = models.FloatField(default=0.0)
    preview = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["message", "document_chunk"],
                name="unique_message_document_chunk_source",
            ),
        ]

    def __str__(self):
        return f"{self.message_id} -> {self.document.title}#{self.document_chunk_id}"
