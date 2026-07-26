from rest_framework import serializers
from .models import Note, Task, Goal


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "related_documents", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "priority", "due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class GoalSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "target_date",
            "deadline",
            "progress",
            "is_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "deadline", "created_at", "updated_at"]

    def get_deadline(self, obj):
        return obj.target_date.isoformat() if obj.target_date else None
