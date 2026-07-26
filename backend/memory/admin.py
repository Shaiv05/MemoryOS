from django.contrib import admin

from .models import MemoryEntry


@admin.register(MemoryEntry)
class MemoryEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "category", "is_pinned", "updated_at"]
    list_filter = ["category", "is_pinned", "source"]
    search_fields = ["title", "content", "owner__email", "owner__username"]
