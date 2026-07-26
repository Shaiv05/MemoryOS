import re
import tiktoken
from django.conf import settings


def count_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Count tokens in a text string using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping abbreviations intact."""
    if not text:
        return []
    
    abbreviations = {
        "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "gen.",
        "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sep.", "oct.", "nov.", "dec.",
        "vs.", "eg.", "ie.", "ca.", "etc.", "approx."
    }
    
    words = text.split()
    sentences = []
    current_sentence = []
    
    for i, word in enumerate(words):
        current_sentence.append(word)
        if word and word[-1] in {".", "!", "?"}:
            # Check if this word is a known abbreviation (case-insensitive)
            if word.lower() in abbreviations:
                continue
            # If the next word exists and starts with a lowercase letter, don't split
            if i + 1 < len(words):
                next_word = words[i + 1]
                if next_word and next_word[0].islower():
                    continue
            
            sentences.append(" ".join(current_sentence))
            current_sentence = []
            
    if current_sentence:
        sentences.append(" ".join(current_sentence))
        
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[dict]:
    """
    Intelligently chunks text by preserving sentence boundaries where possible.
    Returns a list of dictionaries, each containing:
      - 'text': string content of the chunk
      - 'token_count': integer number of tokens in the chunk
      - 'char_count': integer number of characters in the chunk
    """
    if not text or not text.strip():
        return []

    # Fallback to defaults from settings if not specified
    size = chunk_size or getattr(settings, "DOCUMENT_CHUNK_SIZE", 250)
    overlap_size = overlap or getattr(settings, "DOCUMENT_CHUNK_OVERLAP", 50)
    
    # Ensure overlap size is less than chunk size
    if overlap_size >= size:
        overlap_size = max(0, size // 5)

    # First, split into sentences
    sentences = split_into_sentences(text)
    if not sentences:
        return []

    # Encode and prepare list of sentence-tokens pairs
    sentence_tokens = []
    for s in sentences:
        tokens = count_tokens(s)
        # If a single sentence exceeds the chunk_size, split it by words
        if tokens > size:
            words = s.split()
            current_chunk_words = []
            current_tokens = 0
            for w in words:
                # Add 1 space token approximation
                w_tok = count_tokens(w) + 1
                if current_tokens + w_tok > size:
                    if current_chunk_words:
                        wc_text = " ".join(current_chunk_words)
                        sentence_tokens.append((wc_text, count_tokens(wc_text)))
                    current_chunk_words = [w]
                    current_tokens = w_tok
                else:
                    current_chunk_words.append(w)
                    current_tokens += w_tok
            if current_chunk_words:
                wc_text = " ".join(current_chunk_words)
                sentence_tokens.append((wc_text, count_tokens(wc_text)))
        else:
            sentence_tokens.append((s, tokens))

    chunks = []
    current_chunk = []
    current_tokens = 0

    i = 0
    while i < len(sentence_tokens):
        s_text, s_tok = sentence_tokens[i]
        
        # If adding the next sentence exceeds chunk_size
        if current_tokens + s_tok > size:
            if current_chunk:
                chunk_str = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_str,
                    "token_count": count_tokens(chunk_str),
                    "char_count": len(chunk_str)
                })
            
            # Sliding window based on overlap size
            overlap_tokens = 0
            overlap_index = len(current_chunk)
            
            while overlap_index > 0:
                prev_sent_idx = i - (len(current_chunk) - overlap_index + 1)
                if prev_sent_idx < 0:
                    break
                prev_tok = sentence_tokens[prev_sent_idx][1]
                if overlap_tokens + prev_tok > overlap_size:
                    break
                overlap_tokens += prev_tok
                overlap_index -= 1
                
            if overlap_index < len(current_chunk):
                current_chunk = current_chunk[overlap_index:]
                current_tokens = overlap_tokens
            else:
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(s_text)
            current_tokens += s_tok
        else:
            current_chunk.append(s_text)
            current_tokens += s_tok
        i += 1

    if current_chunk:
        chunk_str = " ".join(current_chunk)
        chunks.append({
            "text": chunk_str,
            "token_count": count_tokens(chunk_str),
            "char_count": len(chunk_str)
        })

    return chunks
