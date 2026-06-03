from django.conf import settings
from django.db import models


class MemoryEntry(models.Model):
    CATEGORY_FACT = "fact"
    CATEGORY_PREFERENCE = "preference"
    CATEGORY_SUMMARY = "summary"
    CATEGORY_NOTE = "note"
    CATEGORY_PINNED = "pinned"

    CATEGORY_CHOICES = [
        (CATEGORY_FACT, "Fact"),
        (CATEGORY_PREFERENCE, "Preference"),
        (CATEGORY_SUMMARY, "Summary"),
        (CATEGORY_NOTE, "Note"),
        (CATEGORY_PINNED, "Pinned"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memory_entries",
    )
    title = models.CharField(max_length=180)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_NOTE,
    )
    tags = models.JSONField(default=list, blank=True)
    is_pinned = models.BooleanField(default=False)
    source = models.CharField(max_length=120, blank=True, default="manual")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["owner", "category"], name="memory_owner_category_idx"),
            models.Index(fields=["owner", "-updated_at"], name="memory_owner_updated_idx"),
            models.Index(fields=["owner", "is_pinned"], name="memory_owner_pinned_idx"),
        ]

    def __str__(self):
        return self.title
