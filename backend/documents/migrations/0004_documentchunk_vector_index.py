from django.db import migrations, models
from pgvector.django import HnswIndex


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_document_processing_fields"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="documentchunk",
            constraint=models.UniqueConstraint(
                fields=("document", "chunk_index"),
                name="unique_document_chunk_index",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["owner", "processing_status"],
                name="doc_owner_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["owner", "-created_at"],
                name="doc_owner_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="documentchunk",
            index=models.Index(
                fields=["document", "chunk_index"],
                name="chunk_document_order_idx",
            ),
        ),
    ]
