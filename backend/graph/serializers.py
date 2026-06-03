from rest_framework import serializers
from .models import Node, Edge


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = [
            "id",
            "title",
            "node_type",
            "description",
            "metadata",
            "created_at",
            "updated_at",
        ]


class EdgeSerializer(serializers.ModelSerializer):
    source_title = serializers.CharField(source="source.title", read_only=True)
    target_title = serializers.CharField(source="target.title", read_only=True)

    class Meta:
        model = Edge
        fields = [
            "id",
            "source",
            "target",
            "source_title",
            "target_title",
            "relationship_type",
            "description",
            "weight",
            "created_at",
        ]


class GraphSerializer(serializers.Serializer):
    nodes = NodeSerializer(many=True)
    edges = EdgeSerializer(many=True)
