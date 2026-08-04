import logging
import os
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, *, question: str, context: str, history: str) -> str:
        raise NotImplementedError


class LocalGroundedProvider(AIProvider):
    """
    Local grounded provider used when no remote API key (e.g. OpenAI) is configured.
    Presents the full, cleanly formatted answer from retrieved document context blocks.
    """

    def generate_response(self, *, question: str, context: str, history: str) -> str:
        if not context or not context.strip():
            return (
                "I could not find relevant processed document context for this question. "
                "Please upload or reprocess your documents, then try again."
            )

        # Parse context blocks formatted by ContextBuilder
        blocks = [b.strip() for b in context.split("\n\n") if b.strip()]
        if not blocks:
            return f"No relevant content found for '{question}'."

        # Filter out memory headers
        doc_blocks = [b for b in blocks if not b.startswith("--- USER MEMORIES")]
        if not doc_blocks:
            doc_blocks = blocks

        answer_sections = []

        for block in doc_blocks:
            lines = block.splitlines()
            if not lines:
                continue

            # First line is header like "[S1] Document: Title | Page: 1 | Section: Intro"
            header = lines[0]

            # Extract content lines (everything after metadata header lines)
            content_lines = []
            in_content = False
            for line in lines:
                if in_content:
                    content_lines.append(line)
                elif "Relevance:" in line or "Section:" in line or "Page:" in line or line.startswith("[S"):
                    in_content = True

            if not content_lines:
                content_lines = lines[1:] if len(lines) > 1 else lines

            content_text = "\n".join(content_lines).strip()

            # Clean header/footer artifacts if any slipped through
            cleaned_lines = []
            for line in content_text.splitlines():
                stripped = line.strip()
                if re.match(r"(?i)^\s*prepared\s+by\s*:.*$", stripped):
                    continue
                if stripped.lower() in {"distributed system", "distributed systems"}:
                    continue
                cleaned_lines.append(line)

            cleaned_content = "\n".join(cleaned_lines).strip()
            if cleaned_content:
                answer_sections.append(cleaned_content)

        if not answer_sections:
            return f"No relevant content found in document for '{question}'."

        return "\n\n".join(answer_sections)


class OpenAIProvider(AIProvider):
    """OpenAI API provider for complete, grounded RAG answer generation."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_response(self, *, question: str, context: str, history: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        system_prompt = (
            "You are MemoryOS, an intelligent AI assistant grounded in retrieved documents.\n"
            "INSTRUCTIONS:\n"
            "1. Answer the question completely and accurately based ONLY on the provided context.\n"
            "2. If the user asks for a definition, goals, advantages, disadvantages, or characteristics, "
            "provide ALL of them clearly using clean bullet points exactly as presented in the context.\n"
            "3. Do NOT drop, truncate, or summarize away any listed items or bullet points.\n"
            "4. Ignore document headers/footers (like 'Prepared by...', author names, or page numbers).\n"
            "5. Cite source tags inline like [S1], [S2] immediately after relevant statements.\n"
            "6. Do NOT hallucinate facts not present in the context."
        )

        user_prompt = (
            f"Conversation history:\n{history or 'No previous history.'}\n\n"
            f"Retrieved Context:\n{context or 'No context available.'}\n\n"
            f"Question: {question}"
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1500,  # Allow full multi-part answer completions
        )
        return response.choices[0].message.content or ""


def get_ai_provider() -> AIProvider:
    provider_name = os.getenv("AI_PROVIDER", "local").lower()
    if provider_name == "openai":
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIProvider(
                api_key=os.environ["OPENAI_API_KEY"],
                model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            )
        logger.warning(
            "AI_PROVIDER=openai requested but OPENAI_API_KEY is missing; "
            "falling back to LocalGroundedProvider."
        )
        return LocalGroundedProvider()
    if provider_name not in {"local", "placeholder"}:
        logger.warning("AI_PROVIDER=%s is not recognized; using LocalGroundedProvider.", provider_name)
    return LocalGroundedProvider()
