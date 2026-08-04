from rest_framework import serializers
from .models import Node, Edge


class DocumentMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    file_type = serializers.CharField()


class NodeSerializer(serializers.ModelSerializer):
    source_documents = DocumentMinimalSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            "id",
            "title",
            "node_type",
            "description",
            "metadata",
            "source_documents",
            "notes",
            "created_at",
            "updated_at",
        ]

    def get_notes(self, obj):
        # Return notes linked via source_documents
        notes_data = []
        for doc in obj.source_documents.all():
            for note in doc.notes.all():
                notes_data.append({"id": note.id, "title": note.title})
        return notes_data


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
