from django.db.models import Q

from .models import MemoryEntry


def normalize_tags(tags):
    if tags is None:
        return []

    if isinstance(tags, str):
        tags = tags.split(",")

    normalized = []
    for tag in tags:
        value = str(tag).strip().lower()
        if value and value not in normalized:
            normalized.append(value)
    return normalized[:12]


def memory_entries_for_user(user):
    return MemoryEntry.objects.filter(owner=user)


def search_memory_entries(user, query="", category="", pinned=None):
    queryset = memory_entries_for_user(user)

    if category:
        queryset = queryset.filter(category=category)

    if pinned is not None:
        queryset = queryset.filter(is_pinned=pinned)

    query = (query or "").strip()
    if query:
        lowered_query = query.lower()
        tag_matches = [
            memory_id
            for memory_id, tags in queryset.values_list("id", "tags")
            if any(lowered_query in str(tag).lower() for tag in tags or [])
        ]
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(id__in=tag_matches)
        )

    return queryset.order_by("-is_pinned", "-updated_at")


def create_memory_entry(user, validated_data):
    validated_data["tags"] = normalize_tags(validated_data.get("tags", []))
    return MemoryEntry.objects.create(owner=user, **validated_data)


def update_memory_entry(memory_entry, validated_data):
    if "tags" in validated_data:
        validated_data["tags"] = normalize_tags(validated_data.get("tags"))

    for field, value in validated_data.items():
        setattr(memory_entry, field, value)
    memory_entry.save()
    return memory_entry
