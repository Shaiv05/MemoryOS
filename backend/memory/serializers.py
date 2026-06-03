from rest_framework import serializers

from .models import MemoryEntry
from .services import normalize_tags


class MemoryEntrySerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=40),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = MemoryEntry
        fields = [
            "id",
            "title",
            "content",
            "category",
            "tags",
            "is_pinned",
            "source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "source", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Content is required.")
        return value

    def validate_tags(self, value):
        return normalize_tags(value)
