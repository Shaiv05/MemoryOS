"""
Intelligent Context Compression Engine for RAG.

Enforces strict token efficiency:
- Caps prompt context at 6,000 characters (~1,500 tokens max, 3-5 top chunks).
- Removes duplicate / redundant text snippets across chunks (>70% word overlap).
- Formats rich citation headers: [S1] Page N | Section: Heading | Document: Title
"""

from dataclasses import dataclass
from typing import Optional

from documents.services.retrieval import RetrievalResult

MAX_CONTEXT_CHARS = 10000  # ~2,500 tokens max to allow complete QA answer blocks
MAX_HISTORY_CHARS = 4000  # ~1,000 tokens max for conversation history


@dataclass(frozen=True)
class ContextSource:
    label: str
    chunk_id: int
    chunk_index: int
    document_id: int
    document_title: str
    page_number: Optional[int]
    section_heading: str
    relevance_score: float
    content: str


@dataclass(frozen=True)
class BuiltContext:
    prompt_context: str
    sources: list[ContextSource]
    total_tokens_approx: int
    source_count: int


def truncate_text(value: str, max_chars: int) -> str:
    value = value or ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars].rsplit(' ', 1)[0]}..."


def _text_similarity_ratio(text1: str, text2: str) -> float:
    """Fast word-set Jaccard similarity to detect duplicate context snippets."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


class ContextBuilder:
    def build(
        self,
        retrieval_results: list[RetrievalResult],
        memories: list | None = None,
        max_chars: int = MAX_CONTEXT_CHARS,
    ) -> BuiltContext:
        """
        Build compressed, deduplicated prompt context from hybrid retrieval results.
        """
        # Sort by relevance score descending
        ordered_results = sorted(
            retrieval_results,
            key=lambda r: r.relevance_score,
            reverse=True,
        )

        sources: list[ContextSource] = []
        blocks: list[str] = []
        used_chars = 0
        included_contents: list[str] = []

        # ─── 1. Inject Long-Term User Memories (if present) ─────────────────
        if memories:
            memory_blocks = []
            for m in memories[:3]:  # Top 3 relevant memories max
                memory_blocks.append(f"- [{m.category.upper()}] {m.title}: {m.content}")
            if memory_blocks:
                mem_header = "--- USER MEMORIES & PREFERENCES ---\n" + "\n".join(memory_blocks)
                blocks.append(mem_header)
                used_chars += len(mem_header)

        # ─── 2. Compress & Deduplicate Retrieval Context ────────────────────
        for idx, result in enumerate(ordered_results):
            chunk = result.chunk
            content = (chunk.content or "").strip()
            if not content:
                continue

            # Check for redundancy with already included chunks (>65% Jaccard word overlap)
            is_redundant = any(
                _text_similarity_ratio(content, existing) > 0.65
                for existing in included_contents
            )
            if is_redundant:
                continue

            metadata = chunk.metadata or {}
            page_number = self._extract_page_number(metadata)
            heading = metadata.get("heading") or metadata.get("section") or ""
            label = f"S{len(sources) + 1}"

            # Format rich citation header
            header_parts = [f"[{label}] Document: {chunk.document.title}"]
            if page_number is not None:
                header_parts.append(f"Page: {page_number}")
            if heading:
                header_parts.append(f"Section: {heading}")
            header_parts.append(f"Relevance: {result.relevance_score:.2f}")

            header_str = " | ".join(header_parts)
            block = f"{header_str}\n{content}"

            if used_chars + len(block) > max_chars and len(sources) >= 1:
                # Always allow at least 1 top candidate chunk, then enforce budget
                break

            sources.append(
                ContextSource(
                    label=label,
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    document_id=chunk.document_id,
                    document_title=chunk.document.title,
                    page_number=page_number,
                    section_heading=heading,
                    relevance_score=result.relevance_score,
                    content=truncate_text(content, 1800),
                )
            )
            blocks.append(block)
            included_contents.append(content)
            used_chars += len(block)

        prompt_context = "\n\n".join(blocks)
        approx_tokens = len(prompt_context.split()) * 4 // 3  # rough estimate

        return BuiltContext(
            prompt_context=prompt_context,
            sources=sources,
            total_tokens_approx=approx_tokens,
            source_count=len(sources),
        )

    def _extract_page_number(self, metadata: dict) -> Optional[int]:
        val = metadata.get("page_number") or metadata.get("page")
        if val is not None:
            try:
                return int(val)
            except (TypeError, ValueError):
                pass
        page_nums = metadata.get("page_numbers")
        if isinstance(page_nums, list) and page_nums:
            try:
                return int(page_nums[0])
            except (TypeError, ValueError):
                pass
        return None


def build_history_context(messages) -> str:
    """Format recent conversation history with strict token cap."""
    history = "\n".join(
        f"{message.role}: {message.content}" for message in messages if message.content
    )
    return truncate_text(history, MAX_HISTORY_CHARS)
