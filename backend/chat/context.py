from dataclasses import dataclass

from documents.services.retrieval import RetrievalResult


MAX_CONTEXT_CHARS = 12000
MAX_HISTORY_CHARS = 4000


@dataclass(frozen=True)
class ContextSource:
    label: str
    chunk_id: int
    chunk_index: int
    document_id: int
    document_title: str
    page_number: int | None
    relevance_score: float
    content: str


@dataclass(frozen=True)
class BuiltContext:
    prompt_context: str
    sources: list[ContextSource]


def truncate_text(value: str, max_chars: int) -> str:
    value = value or ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars].rsplit(' ', 1)[0]}..."


class ContextBuilder:
    def build(
        self,
        retrieval_results: list[RetrievalResult],
        memories: list | None = None,
        max_chars: int = MAX_CONTEXT_CHARS,
    ) -> BuiltContext:
        ordered_results = sorted(
            retrieval_results,
            key=lambda result: (
                result.chunk.document_id,
                result.chunk.chunk_index,
                -result.relevance_score,
            ),
        )
        seen_passages = set()
        sources = []
        blocks = []
        used_chars = 0

        # Inject User Long-Term Memories if present
        if memories:
            memory_blocks = []
            for m in memories[:5]:
                memory_blocks.append(f"- [{m.category.upper()}] {m.title}: {m.content}")
            if memory_blocks:
                mem_header = "--- USER MEMORIES & PREFERENCES ---\n" + "\n".join(memory_blocks)
                blocks.append(mem_header)
                used_chars += len(mem_header)

        for result in ordered_results:
            chunk = result.chunk
            content = (chunk.content or "").strip()
            if not content:
                continue
            signature = " ".join(content.lower().split())[:500]
            if signature in seen_passages:
                continue
            seen_passages.add(signature)

            page_number = self._page_number(chunk)
            source = ContextSource(
                label=f"S{len(sources) + 1}",
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                document_id=chunk.document_id,
                document_title=chunk.document.title,
                page_number=page_number,
                relevance_score=result.relevance_score,
                content=truncate_text(content, 1800),
            )
            block = (
                f"[{source.label}] Document: {source.document_title}\n"
                f"Document ID: {source.document_id}\n"
                f"Chunk ID: {source.chunk_id}\n"
                f"Chunk Index: {source.chunk_index}\n"
                f"Page: {source.page_number or 'unknown'}\n"
                f"Relevance: {source.relevance_score:.2f}\n"
                f"{source.content}"
            )
            if used_chars + len(block) > max_chars:
                break
            sources.append(source)
            blocks.append(block)
            used_chars += len(block)

        return BuiltContext(prompt_context="\n\n".join(blocks), sources=sources)

    def _page_number(self, chunk):
        metadata = chunk.metadata or {}
        value = metadata.get("page_number") or metadata.get("page")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None


def build_history_context(messages) -> str:
    history = "\n".join(
        f"{message.role}: {message.content}" for message in messages if message.content
    )
    return truncate_text(history, MAX_HISTORY_CHARS)
