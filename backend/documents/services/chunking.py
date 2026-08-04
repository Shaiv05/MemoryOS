"""
Chunk persistence helper.

Bridges the chunker output (list of dicts) with the DocumentChunk model.
"""

from documents.models import DocumentChunk
from .chunker import count_tokens


def replace_document_chunks(document, chunks):
    """
    Replaces existing document chunks with new ones.
    Accepts list of dicts (from semantic chunker) or list of strings (legacy).
    Stores rich metadata from the chunker.
    """
    # Remove old chunks (cascade will clean up related MessageSource etc.)
    DocumentChunk.objects.filter(document=document).delete()

    chunk_objs = []
    for index, c in enumerate(chunks):
        if isinstance(c, dict):
            text = c["text"]
            tok_cnt = c.get("token_count") or count_tokens(text)
            char_cnt = c.get("char_count") or len(text)
            meta = c.get("metadata") or {}
            # Enrich metadata with document-level info
            meta["document_id"] = document.id
            meta["document_name"] = document.title
            meta["source_file"] = document.file.name if document.file else ""
            meta["chunk_number"] = index
        else:
            text = c
            tok_cnt = count_tokens(text)
            char_cnt = len(text)
            meta = {
                "document_id": document.id,
                "document_name": document.title,
                "chunk_number": index,
            }

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

    created = DocumentChunk.objects.bulk_create(chunk_objs)
    return created
