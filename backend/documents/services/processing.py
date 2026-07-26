# Proxy to document_processor to avoid breaking existing imports
from .document_processor import process_document
from .chunking import chunk_text, replace_document_chunks
from .embeddings import embed_chunks
from .extraction import extract_document_text
