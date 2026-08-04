# Proxy to document_processor to avoid breaking existing imports
from .chunker import chunk_text
from .chunking import replace_document_chunks
from .document_processor import process_document
from .embeddings import embed_chunks
from .extraction import extract_document_text

__all__ = [
    "process_document",
    "chunk_text",
    "replace_document_chunks",
    "embed_chunks",
    "extract_document_text",
]
