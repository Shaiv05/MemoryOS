from dataclasses import dataclass
from typing import Iterable

from django.conf import settings
from django.db.models import Q

from pgvector.django import CosineDistance

from documents.models import DocumentChunk

from .embeddings import embed_query


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    relevance_score: float


def similarity_from_distance(score):
    if score is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 - float(score)))


def _dedupe_chunks(chunks: Iterable[DocumentChunk], limit: int):
    seen = set()
    results = []
    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        results.append(chunk)
        if len(results) >= limit:
            break
    return results


class DocumentRetrievalService:
    def _supports_vector_search(self):
        engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
        return "postgres" in engine or "postgresql" in engine

    def retrieve(self, user, query, limit=5):
        query = (query or "").strip()
        if not query:
            return []

        chunks = self._vector_search(user, query, limit) if self._supports_vector_search() else []
        if not chunks:
            chunks = self._keyword_search(user, query, limit)

        return [
            RetrievalResult(
                chunk=chunk,
                relevance_score=similarity_from_distance(getattr(chunk, "score", None)),
            )
            for chunk in chunks
        ]

    def _vector_search(self, user, query, limit):
        try:
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
        except Exception:
            return []

    def _keyword_search(self, user, query, limit):
        terms = [term for term in query.split() if len(term) > 2]
        q_filter = Q()
        for term in terms[:8]:
            q_filter |= Q(text__icontains=term) | Q(document__title__icontains=term)

        queryset = DocumentChunk.objects.filter(document__owner=user).select_related("document")
        if q_filter:
            queryset = queryset.filter(q_filter)

        chunks = list(queryset.order_by("document_id", "chunk_index")[: limit * 3])
        scored = sorted(
            chunks,
            key=lambda chunk: self._keyword_score(query, chunk),
            reverse=True,
        )
        for chunk in scored:
            chunk.score = 1.0 - self._keyword_score(query, chunk)
        return _dedupe_chunks(scored, limit)

    def _keyword_score(self, query, chunk):
        query_terms = {term.lower() for term in query.split() if len(term) > 2}
        if not query_terms:
            return 0.0
        text = f"{chunk.document.title} {chunk.content}".lower()
        matched = sum(1 for term in query_terms if term in text)
        return matched / len(query_terms)


def retrieve_document_chunks(user, query, limit=5):
    return DocumentRetrievalService().retrieve(user, query, limit=limit)


def search_document_chunks(user, query, limit=5):
    query = (query or "").strip()
    if not query:
        return []

    results = retrieve_document_chunks(user, query, limit=limit)
    chunks = []
    for result in results:
        result.chunk.score = 1.0 - result.relevance_score
        chunks.append(result.chunk)
    return chunks
