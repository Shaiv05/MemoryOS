from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=1)
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=50)
    min_score = serializers.FloatField(required=False, default=0.20, min_value=0.0, max_value=1.0)
    file_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    document_id = serializers.IntegerField(required=False, allow_null=True)
    page = serializers.IntegerField(required=False, default=1, min_value=1)


class SearchResultSerializer(serializers.Serializer):
    chunk_id = serializers.IntegerField(source="id")
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    document_id = serializers.IntegerField(source="document.id")
    document_title = serializers.CharField(source="document.title")
    file_type = serializers.CharField(source="document.file_type")
    similarity_score = serializers.SerializerMethodField()
    relevance_score = serializers.SerializerMethodField()
    metadata = serializers.JSONField()

    def get_similarity_score(self, obj):
        rel = getattr(obj, "relevance_score", None)
        if rel is not None:
            return rel
        score = getattr(obj, "score", None)
        if score is not None:
            return max(0.0, min(1.0, 1.0 - float(score)))
        return 0.0

    def get_relevance_score(self, obj):
        return self.get_similarity_score(obj)
