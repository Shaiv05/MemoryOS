from django.conf import settings
from documents.models import DocumentChunk
from .chunker import chunk_text as intelligent_chunk_text


def chunk_text(text, chunk_size=None, overlap=None):
    """Legacy wrapper for intelligent chunker, returns list of text strings."""
    chunks = intelligent_chunk_text(text, chunk_size, overlap)
    return [c["text"] for c in chunks]


def replace_document_chunks(document, chunks):
    """
    Replaces existing document chunks with new ones.
    Accepts list of strings (legacy) or list of dicts (from intelligent chunker).
    """
    import tiktoken

    def get_token_count(t):
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(t))
        except Exception:
            return len(t.split())

    DocumentChunk.objects.filter(document=document).delete()

    chunk_objs = []
    for index, c in enumerate(chunks):
        if isinstance(c, dict):
            text = c["text"]
            tok_cnt = c.get("token_count") or get_token_count(text)
            char_cnt = c.get("char_count") or len(text)
            meta = c.get("metadata") or {}
        else:
            text = c
            tok_cnt = get_token_count(text)
            char_cnt = len(text)
            meta = {}

        chunk_objs.append(
            DocumentChunk(
                document=document,
                chunk_index=index,
                text=text,
                token_count=tok_cnt,
                char_count=char_cnt,
                metadata=meta,
            )
        )

    return DocumentChunk.objects.bulk_create(chunk_objs)
