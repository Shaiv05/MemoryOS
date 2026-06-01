from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_enable_pgvector_and_documentchunk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="raw_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="document",
            name="processing_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="processing_error",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="document",
            name="extracted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="document",
            name="source_checksum",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
