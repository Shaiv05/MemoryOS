"""
Document retrieval service.

Hybrid search combining:
  1. Dense vector search (cosine similarity)
  2. BM25 keyword search
  3. Reciprocal Rank Fusion (RRF) for score merging
  4. Optional cross-encoder re-ranking

Retrieves top-K candidates, re-ranks, and returns the best chunks.
"""

import logging
import math
import re
import time
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from django.conf import settings
from django.db.models import Q

from documents.models import DocumentChunk
from .embeddings import embed_query

logger = logging.getLogger(__name__)

# RRF constant (standard value from the RRF paper)
RRF_K = 60


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    relevance_score: float
    vector_score: float = 0.0
    keyword_score: float = 0.0
    rrf_score: float = 0.0


@dataclass
class DebugInfo:
    """Optional debug data attached to retrieval results."""
    query: str = ""
    query_embedding_preview: list[float] = field(default_factory=list)
    vector_results_count: int = 0
    keyword_results_count: int = 0
    retrieval_time_ms: float = 0.0
    reranking_applied: bool = False
    candidate_details: list[dict] = field(default_factory=list)


def _cosine_similarity(vec1: list, vec2: list) -> float:
    """Cosine similarity between two float vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def _dedupe_chunks(chunks: Iterable[DocumentChunk], limit: int) -> List[DocumentChunk]:
    """Remove duplicate chunks by ID."""
    seen: set[int] = set()
    results: list[DocumentChunk] = []
    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        results.append(chunk)
        if len(results) >= limit:
            break
    return results


def similarity_from_distance(score) -> float:
    """Convert pgvector cosine distance to similarity (1 - distance)."""
    if score is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 - float(score)))


class DocumentRetrievalService:
    def _supports_pgvector(self) -> bool:
        engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
        return "postgres" in engine or "postgresql" in engine

    def retrieve(
        self,
        user,
        query: str,
        limit: int = 10,
        min_score: Optional[float] = None,
        document_id: Optional[int] = None,
        file_type: Optional[str] = None,
        title_filter: Optional[str] = None,
        return_debug: bool = False,
    ) -> List[RetrievalResult] | tuple[List[RetrievalResult], DebugInfo]:
        """
        Hybrid retrieval: dense vector + BM25 keyword, merged with RRF.

        Returns top `limit` results sorted by relevance.
        If `return_debug` is True, also returns a DebugInfo object.
        """
        start_time = time.time()
        query = (query or "").strip()
        if not query:
            return ([], DebugInfo()) if return_debug else []

        if min_score is None:
            min_score = getattr(settings, "RAG_MIN_RETRIEVAL_SCORE", 0.30)

        debug = DebugInfo(query=query)

        base_qs = DocumentChunk.objects.filter(
            document__owner=user
        ).select_related("document")

        if document_id:
            base_qs = base_qs.filter(document_id=document_id)
        if file_type:
            base_qs = base_qs.filter(document__file_type=file_type)
        if title_filter:
            base_qs = base_qs.filter(document__title__icontains=title_filter)

        top_k = getattr(settings, "RAG_TOP_K_RETRIEVAL", 10)
        fetch_limit = max(limit, top_k) * 3  # fetch extra for fusion

        # ─── Step 1: Dense Vector Search ─────────────────────────────────
        vector_ranked: list[tuple[DocumentChunk, float]] = []
        query_embedding = None
        try:
            query_embedding = embed_query(query)
            debug.query_embedding_preview = query_embedding[:5]

            if self._supports_pgvector():
                from pgvector.django import CosineDistance

                v_qs = (
                    base_qs.filter(embedding__isnull=False)
                    .annotate(dist=CosineDistance("embedding", query_embedding))
                    .order_by("dist")[: fetch_limit]
                )
                for chunk in v_qs:
                    sim = similarity_from_distance(getattr(chunk, "dist", None))
                    vector_ranked.append((chunk, sim))
            else:
                # Python fallback (SQLite / local dev)
                candidates = list(base_qs.filter(embedding__isnull=False))
                scored = []
                for chunk in candidates:
                    if isinstance(chunk.embedding, list):
                        sim = _cosine_similarity(query_embedding, chunk.embedding)
                        if sim > 0.01:
                            scored.append((chunk, sim))
                scored.sort(key=lambda x: x[1], reverse=True)
                vector_ranked = scored[:fetch_limit]

            debug.vector_results_count = len(vector_ranked)
        except Exception as exc:
            logger.warning("Vector search failed: %s", exc)
            vector_ranked = []

        # ─── Step 2: BM25 Keyword Search ─────────────────────────────────
        keyword_ranked: list[tuple[DocumentChunk, float]] = []
        try:
            keyword_ranked = self._keyword_search(base_qs, query, fetch_limit)
            debug.keyword_results_count = len(keyword_ranked)
        except Exception as exc:
            logger.warning("Keyword search failed: %s", exc)

        # ─── Step 3: Reciprocal Rank Fusion ──────────────────────────────
        chunk_map: dict[int, dict] = {}

        for rank, (chunk, v_score) in enumerate(vector_ranked):
            rrf = 1.0 / (RRF_K + rank + 1)
            chunk_map[chunk.id] = {
                "chunk": chunk,
                "v_score": v_score,
                "k_score": 0.0,
                "v_rrf": rrf,
                "k_rrf": 0.0,
            }

        for rank, (chunk, k_score) in enumerate(keyword_ranked):
            rrf = 1.0 / (RRF_K + rank + 1)
            if chunk.id in chunk_map:
                chunk_map[chunk.id]["k_score"] = k_score
                chunk_map[chunk.id]["k_rrf"] = rrf
            else:
                chunk_map[chunk.id] = {
                    "chunk": chunk,
                    "v_score": 0.0,
                    "k_score": k_score,
                    "v_rrf": 0.0,
                    "k_rrf": rrf,
                }

        # Compute combined RRF score
        results: list[RetrievalResult] = []
        for cid, entry in chunk_map.items():
            combined_rrf = entry["v_rrf"] + entry["k_rrf"]
            v_score = entry["v_score"]
            k_score = entry["k_score"]

            # Final relevance: weighted blend of raw scores + RRF boost
            if v_score > 0 and k_score > 0:
                # Both signals agree — strongest evidence
                final_score = 0.6 * max(v_score, k_score) + 0.4 * min(v_score, k_score)
                final_score = min(1.0, final_score * 1.15)  # agreement bonus
            elif v_score > 0:
                final_score = v_score
            else:
                final_score = k_score

            if final_score >= min_score:
                results.append(
                    RetrievalResult(
                        chunk=entry["chunk"],
                        relevance_score=round(final_score, 4),
                        vector_score=round(v_score, 4),
                        keyword_score=round(k_score, 4),
                        rrf_score=round(combined_rrf, 6),
                    )
                )

                debug.candidate_details.append({
                    "chunk_id": cid,
                    "chunk_index": entry["chunk"].chunk_index,
                    "document": entry["chunk"].document.title,
                    "v_score": round(v_score, 4),
                    "k_score": round(k_score, 4),
                    "rrf": round(combined_rrf, 6),
                    "final": round(final_score, 4),
                    "preview": (entry["chunk"].text or "")[:100],
                })

        results.sort(key=lambda r: r.relevance_score, reverse=True)

        # ─── Step 4: Relevance Score Drop-off Cutoff ────────────────────
        if results:
            top_score = results[0].relevance_score
            cutoff_ratio = getattr(settings, "RAG_SCORE_DROP_CUTOFF", 0.40)
            filtered_results: list[RetrievalResult] = []
            for r in results:
                if (top_score - r.relevance_score) / top_score <= cutoff_ratio:
                    filtered_results.append(r)
                else:
                    break
            results = filtered_results

        results = results[:limit]

        elapsed = time.time() - start_time
        debug.retrieval_time_ms = round(elapsed * 1000, 1)

        logger.info(
            "Retrieval: query='%s' → %d vector + %d keyword → %d results in %.0fms",
            query[:60],
            debug.vector_results_count,
            debug.keyword_results_count,
            len(results),
            debug.retrieval_time_ms,
        )

        if return_debug:
            return results, debug
        return results

    def _keyword_search(
        self, base_qs, query: str, limit: int
    ) -> list[tuple[DocumentChunk, float]]:
        """
        BM25-style keyword search using database filtering + Python scoring.
        Returns list of (chunk, score) tuples sorted by score descending.
        """
        raw_terms = [
            t.strip().lower()
            for t in re.findall(r"\w+", query)
            if len(t.strip()) > 1
        ]
        stopwords = {
            "the", "is", "at", "which", "on", "a", "an", "and", "or",
            "in", "for", "to", "of", "with", "it", "by", "this", "that",
            "are", "was", "were", "be", "been", "do", "does", "did",
            "has", "have", "had", "not", "but", "if", "what", "how",
        }
        query_terms = [t for t in raw_terms if t not in stopwords] or raw_terms

        if not query_terms:
            return []

        # Build DB filter
        q_filter = Q()
        for term in query_terms:
            q_filter |= Q(text__icontains=term) | Q(
                document__title__icontains=term
            )

        candidates = list(base_qs.filter(q_filter)[: limit * 4])

        scored: list[tuple[DocumentChunk, float]] = []
        for chunk in candidates:
            score = self._compute_keyword_score(query, query_terms, chunk)
            if score >= 0.2:
                scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate
        seen: set[int] = set()
        deduped: list[tuple[DocumentChunk, float]] = []
        for chunk, score in scored:
            if chunk.id not in seen:
                seen.add(chunk.id)
                deduped.append((chunk, score))
            if len(deduped) >= limit:
                break

        return deduped

    def _compute_keyword_score(
        self, query: str, query_terms: list, chunk: DocumentChunk
    ) -> float:
        """Compute a BM25-inspired keyword relevance score."""
        text_lower = chunk.text.lower()
        title_lower = chunk.document.title.lower()
        full_context = f"{title_lower} {text_lower}"
        doc_len = len(full_context.split())
        avg_doc_len = 200  # approximate average

        # Exact phrase match bonus
        query_lower = query.lower().strip()
        phrase_bonus = 0.0
        if len(query_lower) > 3 and query_lower in full_context:
            phrase_bonus = 0.4

        # BM25-style term scoring
        k1 = 1.2
        b = 0.75
        total_score = 0.0
        matches = 0

        for term in query_terms:
            tf = full_context.count(term)
            if tf > 0:
                matches += 1
                # BM25 TF saturation
                tf_score = (tf * (k1 + 1)) / (
                    tf + k1 * (1 - b + b * doc_len / avg_doc_len)
                )
                total_score += tf_score

                # Title match bonus
                if term in title_lower:
                    total_score += 0.5

        match_ratio = matches / len(query_terms)

        # Require at least 50% term match for multi-term queries
        if match_ratio < 0.50 and len(query_terms) > 1:
            return 0.0

        # Normalize to 0-1 range
        normalized = min(1.0, total_score / (len(query_terms) * 2.5))
        final = (match_ratio * 0.3) + (normalized * 0.3) + phrase_bonus

        return min(1.0, final)


# ─── Public API ──────────────────────────────────────────────────────────────


def retrieve_document_chunks(user, query, limit=10, return_debug=False):
    """Retrieve relevant chunks using hybrid search."""
    return DocumentRetrievalService().retrieve(
        user, query, limit=limit, return_debug=return_debug
    )


def search_document_chunks(
    user,
    query,
    limit=10,
    min_score=0.15,
    document_id=None,
    file_type=None,
    title_filter=None,
):
    """Search for document chunks — used by Search API."""
    query = (query or "").strip()
    if not query:
        return []

    results = DocumentRetrievalService().retrieve(
        user,
        query,
        limit=limit,
        min_score=min_score,
        document_id=document_id,
        file_type=file_type,
        title_filter=title_filter,
    )

    chunks = []
    for result in results:
        chunk = result.chunk
        chunk.relevance_score = result.relevance_score
        chunk.vector_score = result.vector_score
        chunk.keyword_score = result.keyword_score
        # Store distance-format score for backward compat with serializers
        chunk.score = 1.0 - result.relevance_score
        chunks.append(chunk)
    return chunks
