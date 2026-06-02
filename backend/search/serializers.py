from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=1)
    limit = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)


class SearchResultSerializer(serializers.Serializer):
    chunk_id = serializers.IntegerField(source="id")
    chunk_index = serializers.IntegerField()
    content = serializers.CharField()
    document_id = serializers.IntegerField(source="document.id")
    document_title = serializers.CharField(source="document.title")
    similarity_score = serializers.SerializerMethodField()

    def get_similarity_score(self, obj):
        score = getattr(obj, "score", None)
        if score is not None:
            # CosineDistance range is 0 (closest) to 2 (furthest).
            # We convert to a similarity score of 1 (closest) to 0 (furthest).
            return max(0.0, min(1.0, 1.0 - float(score)))
        return 0.0
