"""
Embedding generation module.

Uses sentence-transformers for dense vector embeddings.
All errors are logged (never silently swallowed).
Supports batch embedding with configurable batch size.
"""

import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)


class EmbeddingError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the sentence-transformer model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbeddingError(
            "sentence-transformers is not installed. "
            "Run pip install -r requirements.txt."
        ) from exc

    model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Loading embedding model: %s", model_name)
    model = SentenceTransformer(model_name)
    logger.info(
        "Embedding model loaded: %s (dim=%d)",
        model_name,
        model.get_sentence_embedding_dimension(),
    )
    return model


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """
    Generate normalized embeddings for a list of texts.
    Returns list of float vectors.  Raises EmbeddingError on failure.
    """
    if not texts:
        return []

    try:
        model = get_embedding_model()
        embeddings = model.encode(
            list(texts),
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=False,
        )
        result = [embedding.tolist() for embedding in embeddings]

        # Validate dimensions
        expected_dim = getattr(settings, "EMBEDDING_DIMENSIONS", 384)
        for idx, emb in enumerate(result):
            if len(emb) != expected_dim:
                logger.error(
                    "Embedding dimension mismatch at index %d: got %d, expected %d",
                    idx, len(emb), expected_dim,
                )
            if all(v == 0.0 for v in emb):
                logger.warning("Zero-vector embedding at index %d", idx)

        logger.info("Generated %d embeddings (dim=%d)", len(result), expected_dim)
        return result

    except EmbeddingError:
        raise
    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc, exc_info=True)
        raise EmbeddingError(f"Embedding generation failed: {exc}") from exc


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query string."""
    if not query or not query.strip():
        raise EmbeddingError("Cannot embed empty query.")
    embeddings = embed_texts([query.strip()])
    if not embeddings:
        raise EmbeddingError("Query embedding returned empty result.")
    return embeddings[0]


def embed_chunks(chunks):
    """
    Generate and persist embeddings for a queryset of DocumentChunk objects.
    Skips chunks with empty text and logs failures.
    """
    chunk_list = list(chunks)
    if not chunk_list:
        logger.info("No chunks to embed.")
        return chunk_list

    # Filter out chunks with empty content
    valid_chunks = [c for c in chunk_list if (c.content or "").strip()]
    if not valid_chunks:
        logger.warning("All %d chunks have empty content — skipping embedding.", len(chunk_list))
        return chunk_list

    skipped = len(chunk_list) - len(valid_chunks)
    if skipped > 0:
        logger.warning("Skipping %d chunks with empty content.", skipped)

    texts = [chunk.content for chunk in valid_chunks]

    try:
        embeddings = embed_texts(texts)
    except EmbeddingError as exc:
        logger.error(
            "Failed to embed %d chunks: %s", len(valid_chunks), exc
        )
        raise

    embedded_count = 0
    for chunk, embedding in zip(valid_chunks, embeddings):
        chunk.embedding = embedding
        embedded_count += 1

    if valid_chunks and embeddings:
        model_class = valid_chunks[0].__class__
        model_class.objects.bulk_update(valid_chunks, ["embedding"])
        logger.info("Persisted %d embeddings to database.", embedded_count)

    return chunk_list
