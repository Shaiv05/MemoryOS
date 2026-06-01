from functools import lru_cache

from django.conf import settings


class EmbeddingError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbeddingError(
            "sentence-transformers is not installed. Run pip install -r requirements.txt."
        ) from exc

    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def embed_texts(texts):
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(list(texts), normalize_embeddings=True)
    return [embedding.tolist() for embedding in embeddings]


def embed_query(query):
    embeddings = embed_texts([query])
    if not embeddings:
        raise EmbeddingError("Query embedding failed.")
    return embeddings[0]


def embed_chunks(chunks):
    chunk_list = list(chunks)
    embeddings = embed_texts([chunk.content for chunk in chunk_list])

    for chunk, embedding in zip(chunk_list, embeddings):
        chunk.embedding = embedding

    if chunk_list:
        chunk_list[0].__class__.objects.bulk_update(chunk_list, ["embedding"])

    return chunk_list
