from pgvector.django import CosineDistance

from documents.models import DocumentChunk

from .embeddings import embed_query


def search_document_chunks(user, query, limit=5):
    query = (query or "").strip()
    if not query:
        return []

    embedding = embed_query(query)
    return list(
        DocumentChunk.objects.filter(
            document__owner=user,
            embedding__isnull=False,
        )
        .select_related("document")
        .annotate(score=CosineDistance("embedding", embedding))
        .order_by("score")[:limit]
    )
