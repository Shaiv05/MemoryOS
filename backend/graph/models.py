from django.conf import settings
from django.db import models

from documents.models import Document


class Node(models.Model):
    NODE_TYPES = [
        ("person", "Person"),
        ("project", "Project"),
        ("company", "Company"),
        ("technology", "Technology"),
        ("topic", "Topic"),
        ("concept", "Concept"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="graph_nodes",
    )
    title = models.CharField(max_length=255)
    node_type = models.CharField(max_length=50, choices=NODE_TYPES, default="topic")
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    source_documents = models.ManyToManyField(Document, blank=True, related_name="entities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("owner", "title", "node_type")
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.node_type})"


class Edge(models.Model):
    RELATIONSHIP_TYPES = [
        ("works_on", "Works On"),
        ("uses", "Uses"),
        ("belongs_to", "Belongs To"),
        ("references", "References"),
        ("related_to", "Related To"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="graph_edges",
    )
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="outgoing_edges")
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="incoming_edges")
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES, default="related_to")
    description = models.TextField(blank=True, default="")
    weight = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "source", "target", "relationship_type")

    def __str__(self):
        return f"{self.source.title} --[{self.relationship_type}]--> {self.target.title}"
