from rest_framework import serializers

from .models import Document
from .validators import validate_document_input


class MultipartFileField(serializers.FileField):
    def to_internal_value(self, data):
        if data in (None, ""):
            return None
        if hasattr(data, "read"):
            return data
        return super().to_internal_value(data)


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.IntegerField(source="chunks.count", read_only=True)
    raw_text_preview = serializers.SerializerMethodField()
    processing_duration = serializers.SerializerMethodField()
    file = MultipartFileField(required=False, allow_null=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "file_type",
            "source_url",
            "raw_text",
            "raw_text_preview",
            "processing_status",
            "processing_error",
            "extracted_at",
            "chunk_count",
            "file_size",
            "page_count",
            "processing_started_at",
            "processing_completed_at",
            "processing_duration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "raw_text_preview",
            "processing_status",
            "processing_error",
            "extracted_at",
            "chunk_count",
            "file_size",
            "page_count",
            "processing_started_at",
            "processing_completed_at",
            "processing_duration",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "raw_text": {"required": False, "allow_blank": True, "write_only": True},
            "file": {"required": False, "allow_null": True},
            "source_url": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def get_raw_text_preview(self, obj):
        text = obj.raw_text or ""
        return text[:500]

    def get_processing_duration(self, obj):
        if obj.processing_started_at and obj.processing_completed_at:
            return (obj.processing_completed_at - obj.processing_started_at).total_seconds()
        elif obj.processing_status == "processing" and obj.processing_started_at:
            from django.utils import timezone
            return (timezone.now() - obj.processing_started_at).total_seconds()
        return None

    def validate(self, attrs):
        attrs = dict(attrs)
        if "file_type" not in attrs and self.instance is not None:
            attrs["file_type"] = self.instance.file_type
        if "raw_text" not in attrs and self.instance is not None:
            attrs["raw_text"] = self.instance.raw_text
        if "source_url" not in attrs and self.instance is not None:
            attrs["source_url"] = self.instance.source_url
        return validate_document_input(attrs, instance=self.instance)


class DocumentSearchResultSerializer(serializers.Serializer):
    chunk_id = serializers.IntegerField(source="id")
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    document_id = serializers.IntegerField(source="document.id")
    document_title = serializers.CharField(source="document.title")
    similarity_score = serializers.SerializerMethodField()

    def get_similarity_score(self, obj):
        score = getattr(obj, "score", None)
        if score is not None:
            return max(0.0, min(1.0, 1.0 - float(score)))
        return 0.0
