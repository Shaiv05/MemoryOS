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
    class Meta:
        model = Goal
        fields = ["id", "title", "description", "target_date", "progress", "is_completed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
