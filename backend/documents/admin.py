from django.contrib import admin

from .models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "file_type",
        "processing_status",
        "chunk_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("file_type", "processing_status", "created_at")
    search_fields = ("title", "owner__username", "source_url")
    readonly_fields = ("created_at", "updated_at", "extracted_at", "chunk_count")

    def chunk_count(self, obj):
        return obj.chunks.count()


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "created_at")
    list_filter = ("created_at",)
    search_fields = ("document__title", "content")
