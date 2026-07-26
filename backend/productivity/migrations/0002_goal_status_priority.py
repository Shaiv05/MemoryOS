from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("productivity", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="goal",
            name="priority",
            field=models.CharField(
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                default="medium",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="goal",
            name="status",
            field=models.CharField(
                choices=[
                    ("planned", "Planned"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("paused", "Paused"),
                ],
                default="planned",
                max_length=20,
            ),
        ),
    ]
