from django.conf import settings

from documents.models import DocumentChunk


def chunk_text(text, chunk_size=None, overlap=None):
    if not text:
        return []

    words = text.split()
    if not words:
        return []

    size = chunk_size or settings.DOCUMENT_CHUNK_SIZE
    overlap_size = overlap or settings.DOCUMENT_CHUNK_OVERLAP
    if overlap_size >= size:
        overlap_size = max(0, size // 5)

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap_size)

    return [chunk for chunk in chunks if chunk]


def replace_document_chunks(document, chunks):
    DocumentChunk.objects.filter(document=document).delete()
    return DocumentChunk.objects.bulk_create(
        [
            DocumentChunk(
                document=document,
                chunk_index=index,
                content=content,
            )
            for index, content in enumerate(chunks)
        ]
    )
