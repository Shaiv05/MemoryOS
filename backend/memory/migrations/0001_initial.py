import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MemoryEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=180)),
                ("content", models.TextField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("fact", "Fact"),
                            ("preference", "Preference"),
                            ("summary", "Summary"),
                            ("note", "Note"),
                            ("pinned", "Pinned"),
                        ],
                        default="note",
                        max_length=20,
                    ),
                ),
                ("tags", models.JSONField(blank=True, default=list)),
                ("is_pinned", models.BooleanField(default=False)),
                ("source", models.CharField(blank=True, default="manual", max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memory_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-is_pinned", "-updated_at"],
            },
        ),
        migrations.AddIndex(
            model_name="memoryentry",
            index=models.Index(
                fields=["owner", "category"],
                name="memory_owner_category_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="memoryentry",
            index=models.Index(
                fields=["owner", "-updated_at"],
                name="memory_owner_updated_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="memoryentry",
            index=models.Index(
                fields=["owner", "is_pinned"],
                name="memory_owner_pinned_idx",
            ),
        ),
    ]
