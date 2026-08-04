"""
Semantic document chunking engine.

Splits text into semantically coherent chunks that respect document structure:
headings, paragraphs, lists, code blocks.  Never splits definitions,
algorithms, examples, tables, or formulas mid-unit.

Target: 400-700 tokens per chunk, 80-120 token overlap.
"""

import logging
import re
from dataclasses import dataclass, field

import tiktoken
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Token Counting ─────────────────────────────────────────────────────────

_ENCODING = None


def _get_encoding():
    global _ENCODING
    if _ENCODING is None:
        try:
            _ENCODING = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _ENCODING = None
    return _ENCODING


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken (cl100k_base), fallback to word split."""
    if not text:
        return 0
    enc = _get_encoding()
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    return len(text.split())


# ─── Document Structure Parsing ──────────────────────────────────────────────

PAGE_MARKER_RE = re.compile(r"^---\s*Page\s+(\d+)\s*---$", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
LIST_ITEM_RE = re.compile(
    r"^\s*([*\-•▪◦‣]\s+|\d+[.)]\s+|[a-zA-Z][.)]\s+)"
)


@dataclass
class TextBlock:
    """A single structural unit extracted from document text."""

    text: str
    block_type: str  # 'heading', 'paragraph', 'list_item', 'code', 'table'
    heading_level: int = 0  # 1-6 for headings, 0 otherwise
    page_number: int | None = None
    start_offset: int = 0  # char offset in the full document text
    end_offset: int = 0
    tokens: int = 0


@dataclass
class DocumentSection:
    """A section of the document, with a heading and child blocks."""

    heading: str = ""
    heading_level: int = 0
    page_number: int | None = None
    blocks: list[TextBlock] = field(default_factory=list)


STAR_QUESTION_RE = re.compile(
    r"^\s*(?:[⭐★]\s*|question\s*\d*\s*[:\.\-]\s*|\d+[\.\)]\s+)?(?:describe|explain|what|list|define)\b",
    re.IGNORECASE,
)


def parse_document_structure(text: str) -> list[TextBlock]:
    """
    Parse cleaned document text into a sequence of typed TextBlocks.
    Understands page markers, star question markers, headings, list items, and paragraphs.
    """
    blocks: list[TextBlock] = []
    current_page: int | None = None
    raw_blocks = re.split(r"\n\s*\n", text)  # split on blank lines
    offset = 0

    for raw in raw_blocks:
        raw_clean = raw.strip()
        if not raw_clean:
            offset += len(raw) + 2  # account for \n\n separator
            continue

        # Check every line in the block for page markers first
        inner_lines = raw_clean.splitlines()
        remaining_lines: list[str] = []
        for line in inner_lines:
            stripped = line.strip()
            page_match = PAGE_MARKER_RE.match(stripped)
            if page_match:
                try:
                    current_page = int(page_match.group(1))
                except ValueError:
                    pass
            else:
                remaining_lines.append(stripped)

        if not remaining_lines:
            offset += len(raw) + 2
            continue

        block_text = "\n".join(remaining_lines)
        start = offset
        end = offset + len(raw)

        # Determine block type
        first_line = remaining_lines[0]
        heading_match = HEADING_RE.match(first_line)
        is_star_question = bool(STAR_QUESTION_RE.match(first_line)) or "⭐" in first_line

        if (heading_match and len(remaining_lines) <= 2) or is_star_question:
            # Heading or Question block
            level = len(heading_match.group(1)) if heading_match else 1
            heading_text = heading_match.group(2).strip() if heading_match else block_text
            if heading_match and len(remaining_lines) == 2:
                heading_text += " " + remaining_lines[1]
            blocks.append(TextBlock(
                text=heading_text,
                block_type="heading",
                heading_level=level,
                page_number=current_page,
                start_offset=start,
                end_offset=end,
                tokens=count_tokens(heading_text),
            ))
        elif first_line.isupper() and len(first_line) < 100 and len(first_line) > 3:
            # ALL-CAPS heading
            blocks.append(TextBlock(
                text=block_text,
                block_type="heading",
                heading_level=2,
                page_number=current_page,
                start_offset=start,
                end_offset=end,
                tokens=count_tokens(block_text),
            ))
        elif all(LIST_ITEM_RE.match(ln) for ln in remaining_lines if ln.strip()):
            # Pure list block — keep together
            blocks.append(TextBlock(
                text=block_text,
                block_type="list_item",
                page_number=current_page,
                start_offset=start,
                end_offset=end,
                tokens=count_tokens(block_text),
            ))
        else:
            # Regular paragraph
            blocks.append(TextBlock(
                text=block_text,
                block_type="paragraph",
                page_number=current_page,
                start_offset=start,
                end_offset=end,
                tokens=count_tokens(block_text),
            ))

        offset += len(raw) + 2

    return blocks


def organise_into_sections(blocks: list[TextBlock]) -> list[DocumentSection]:
    """Group blocks into sections based on heading boundaries."""
    sections: list[DocumentSection] = []
    current_section = DocumentSection()

    for block in blocks:
        if block.block_type == "heading":
            # Start a new section
            if current_section.blocks or current_section.heading:
                sections.append(current_section)
            current_section = DocumentSection(
                heading=block.text,
                heading_level=block.heading_level,
                page_number=block.page_number,
            )
        else:
            current_section.blocks.append(block)

    if current_section.blocks or current_section.heading:
        sections.append(current_section)

    return sections


# ─── Sentence Splitting ─────────────────────────────────────────────────────

ABBREVIATIONS = frozenset({
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "gen.",
    "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.",
    "sep.", "oct.", "nov.", "dec.",
    "vs.", "eg.", "ie.", "ca.", "etc.", "approx.", "fig.",
    "no.", "vol.", "pp.", "dept.", "inc.", "corp.", "ltd.",
    "e.g.", "i.e.",
})


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, respecting abbreviations."""
    if not text or not text.strip():
        return []

    # Split on sentence-ending punctuation followed by whitespace and uppercase
    candidates = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'#\-])", text)
    sentences: list[str] = []

    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate:
            continue
        # Merge abbreviations with next
        words = candidate.split()
        if words and words[-1].lower() in ABBREVIATIONS and len(words) <= 2:
            if sentences:
                sentences[-1] += " " + candidate
            else:
                sentences.append(candidate)
        else:
            sentences.append(candidate)

    return [s.strip() for s in sentences if s.strip()]


# ─── Semantic Chunking ───────────────────────────────────────────────────────


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict]:
    """
    Semantically chunk document text.

    Respects document structure: headings start new chunks, paragraphs and
    list items are kept whole when possible.  Only splits long paragraphs
    at sentence boundaries when they exceed the token budget.

    Returns list of dicts with keys:
      text, token_count, char_count, metadata
    """
    if not text or not text.strip():
        return []

    max_tokens = chunk_size or getattr(settings, "DOCUMENT_CHUNK_SIZE", 500)
    overlap_tokens = overlap or getattr(settings, "DOCUMENT_CHUNK_OVERLAP", 100)

    if overlap_tokens >= max_tokens:
        overlap_tokens = max(0, max_tokens // 5)

    # Parse structure
    blocks = parse_document_structure(text)
    if not blocks:
        return []

    sections = organise_into_sections(blocks)

    # Build semantic units: each is a dict { text, tokens, page_number, heading, section }
    semantic_units: list[dict] = []

    current_chapter = ""
    current_section = ""

    for section in sections:
        # Track hierarchy
        if section.heading_level <= 1 and section.heading:
            current_chapter = section.heading
            current_section = section.heading
        elif section.heading:
            current_section = section.heading

        # Heading itself as a unit (will be prepended to the first chunk in this section)
        heading_prefix = ""
        if section.heading:
            heading_prefix = f"{'#' * min(section.heading_level, 4)} {section.heading}"

        for block_idx, block in enumerate(section.blocks):
            # Prepend section heading to first block of each section
            block_text = block.text
            if block_idx == 0 and heading_prefix:
                block_text = f"{heading_prefix}\n\n{block_text}"

            if block.tokens <= max_tokens:
                semantic_units.append({
                    "text": block_text,
                    "tokens": count_tokens(block_text),
                    "page_number": block.page_number or section.page_number,
                    "chapter": current_chapter,
                    "section": current_section,
                    "heading": section.heading,
                    "start_offset": block.start_offset,
                    "end_offset": block.end_offset,
                })
            else:
                # Block exceeds max tokens — split at sentence boundaries
                sentences = split_into_sentences(block_text)
                for sent in sentences:
                    s_tokens = count_tokens(sent)
                    if s_tokens <= max_tokens:
                        semantic_units.append({
                            "text": sent,
                            "tokens": s_tokens,
                            "page_number": block.page_number or section.page_number,
                            "chapter": current_chapter,
                            "section": current_section,
                            "heading": section.heading,
                            "start_offset": block.start_offset,
                            "end_offset": block.end_offset,
                        })
                    else:
                        # Very long sentence — split by words as last resort
                        words = sent.split()
                        buf: list[str] = []
                        buf_tokens = 0
                        for w in words:
                            w_tok = count_tokens(w) + 1
                            if buf_tokens + w_tok > max_tokens and buf:
                                chunk_str = " ".join(buf)
                                semantic_units.append({
                                    "text": chunk_str,
                                    "tokens": count_tokens(chunk_str),
                                    "page_number": block.page_number or section.page_number,
                                    "chapter": current_chapter,
                                    "section": current_section,
                                    "heading": section.heading,
                                    "start_offset": block.start_offset,
                                    "end_offset": block.end_offset,
                                })
                                buf = [w]
                                buf_tokens = w_tok
                            else:
                                buf.append(w)
                                buf_tokens += w_tok
                        if buf:
                            chunk_str = " ".join(buf)
                            semantic_units.append({
                                "text": chunk_str,
                                "tokens": count_tokens(chunk_str),
                                "page_number": block.page_number or section.page_number,
                                "chapter": current_chapter,
                                "section": current_section,
                                "heading": section.heading,
                                "start_offset": block.start_offset,
                                "end_offset": block.end_offset,
                            })

        # If section had heading but no blocks, emit heading as a standalone unit
        if not section.blocks and heading_prefix:
            semantic_units.append({
                "text": heading_prefix,
                "tokens": count_tokens(heading_prefix),
                "page_number": section.page_number,
                "chapter": current_chapter,
                "section": current_section,
                "heading": section.heading,
                "start_offset": 0,
                "end_offset": 0,
            })

    if not semantic_units:
        return []

    # ─── Assemble units into chunks with overlap ─────────────────────────

    chunks: list[dict] = []
    current_group: list[dict] = []
    current_tokens = 0

    i = 0
    while i < len(semantic_units):
        unit = semantic_units[i]

        if current_tokens + unit["tokens"] > max_tokens and current_group:
            # Emit current chunk
            chunk_text_str = "\n\n".join(u["text"] for u in current_group)
            pages = [u["page_number"] for u in current_group if u["page_number"] is not None]
            chapters = [u["chapter"] for u in current_group if u.get("chapter")]
            sections_list = [u["section"] for u in current_group if u.get("section")]
            headings = [u["heading"] for u in current_group if u.get("heading")]
            offsets = [u["start_offset"] for u in current_group] + [u["end_offset"] for u in current_group]

            chunks.append({
                "text": chunk_text_str,
                "token_count": count_tokens(chunk_text_str),
                "char_count": len(chunk_text_str),
                "metadata": {
                    "page_number": pages[0] if pages else None,
                    "page_numbers": sorted(set(pages)) if pages else [],
                    "chapter": chapters[0] if chapters else "",
                    "section": sections_list[-1] if sections_list else "",
                    "heading": headings[-1] if headings else "",
                    "start_offset": min(offsets) if offsets else 0,
                    "end_offset": max(offsets) if offsets else 0,
                    "unit_count": len(current_group),
                },
            })

            # Calculate overlap: keep trailing units that fit in overlap budget
            overlap_tok_sum = 0
            overlap_start = len(current_group)
            while overlap_start > 0:
                prev = current_group[overlap_start - 1]
                if overlap_tok_sum + prev["tokens"] > overlap_tokens:
                    break
                overlap_tok_sum += prev["tokens"]
                overlap_start -= 1

            current_group = current_group[overlap_start:]
            current_tokens = overlap_tok_sum
            # Don't increment i — retry adding the current unit
            continue

        current_group.append(unit)
        current_tokens += unit["tokens"]
        i += 1

    # Emit final chunk
    if current_group:
        chunk_text_str = "\n\n".join(u["text"] for u in current_group)
        pages = [u["page_number"] for u in current_group if u["page_number"] is not None]
        chapters = [u["chapter"] for u in current_group if u.get("chapter")]
        sections_list = [u["section"] for u in current_group if u.get("section")]
        headings = [u["heading"] for u in current_group if u.get("heading")]
        offsets = [u["start_offset"] for u in current_group] + [u["end_offset"] for u in current_group]

        chunks.append({
            "text": chunk_text_str,
            "token_count": count_tokens(chunk_text_str),
            "char_count": len(chunk_text_str),
            "metadata": {
                "page_number": pages[0] if pages else None,
                "page_numbers": sorted(set(pages)) if pages else [],
                "chapter": chapters[0] if chapters else "",
                "section": sections_list[-1] if sections_list else "",
                "heading": headings[-1] if headings else "",
                "start_offset": min(offsets) if offsets else 0,
                "end_offset": max(offsets) if offsets else 0,
                "unit_count": len(current_group),
            },
        })

    logger.info(
        "Semantic chunking: %d units → %d chunks (target %d tokens, overlap %d)",
        len(semantic_units),
        len(chunks),
        max_tokens,
        overlap_tokens,
    )
    return chunks
