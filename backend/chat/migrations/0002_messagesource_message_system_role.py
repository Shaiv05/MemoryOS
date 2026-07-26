import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
        ("documents", "0005_rename_content_documentchunk_text_document_file_size_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="role",
            field=models.CharField(
                choices=[
                    ("system", "System"),
                    ("user", "User"),
                    ("assistant", "Assistant"),
                ],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="MessageSource",
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
                ("page_number", models.IntegerField(blank=True, null=True)),
                ("relevance_score", models.FloatField(default=0.0)),
                ("preview", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="message_sources",
                        to="documents.document",
                    ),
                ),
                (
                    "document_chunk",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="message_sources",
                        to="documents.documentchunk",
                    ),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sources",
                        to="chat.message",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddConstraint(
            model_name="messagesource",
            constraint=models.UniqueConstraint(
                fields=("message", "document_chunk"),
                name="unique_message_document_chunk_source",
            ),
        ),
    ]
