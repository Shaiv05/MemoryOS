from rest_framework import serializers

from .models import Conversation, Message
from .services import serialize_message_sources


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
    page_number = serializers.IntegerField(allow_null=True)
    content = serializers.CharField()
    preview = serializers.CharField()
    score = serializers.FloatField()
    similarity_score = serializers.FloatField()
    relevance_score = serializers.FloatField()


class ChatResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    user_message_id = serializers.IntegerField(required=False)
    message_id = serializers.IntegerField()
    answer = serializers.CharField()
    sources = ChatSourceSerializer(many=True)


class ConversationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)


class ConversationRenameSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True, max_length=255)


class ChatMessageSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "role", "content", "sources", "created_at"]

    def get_sources(self, obj):
        if obj.role != "assistant":
            return []
        return serialize_message_sources(obj)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "messages", "created_at", "updated_at"]
