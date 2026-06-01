from rest_framework import serializers

from .models import Document
from .validators import validate_document_input


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.IntegerField(source="chunks.count", read_only=True)
    raw_text_preview = serializers.SerializerMethodField()

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

    def validate(self, attrs):
        return validate_document_input(attrs, instance=self.instance)


class DocumentSearchResultSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    chunk_id = serializers.IntegerField()
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    score = serializers.FloatField()
