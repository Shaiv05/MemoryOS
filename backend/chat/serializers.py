from rest_framework import serializers

from .models import Conversation, Message
from .services import serialize_chunk_sources


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=8000,
    )
    conversation_id = serializers.IntegerField(required=False, min_value=1)


class ChatSourceSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    chunk_id = serializers.IntegerField()
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    score = serializers.FloatField()
    similarity_score = serializers.FloatField()


class ChatResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    message_id = serializers.IntegerField()
    answer = serializers.CharField()
    sources = ChatSourceSerializer(many=True)


class ChatMessageSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "role", "content", "sources", "created_at"]

    def get_sources(self, obj):
        if obj.role != "assistant":
            return []
        chunks = obj.cited_chunks.select_related("document").all()
        return serialize_chunk_sources(chunks)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "messages", "created_at", "updated_at"]
