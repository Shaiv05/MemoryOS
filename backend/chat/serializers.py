from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)


class ChatSourceSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    chunk_id = serializers.IntegerField()
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    score = serializers.FloatField()


class ChatResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    answer = serializers.CharField()
    sources = ChatSourceSerializer(many=True)
