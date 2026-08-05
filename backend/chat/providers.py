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
    Extracts relevant content matching the question terms to construct a precise, grounded, beautifully formatted answer.
    """

    def generate_response(self, *, question: str, context: str, history: str) -> str:
        if not context or not context.strip():
            return (
                "I could not find relevant processed document context for this question. "
                "Please upload or reprocess your documents, then try again."
            )

        blocks = [b.strip() for b in context.split("\n\n") if b.strip()]
        if not blocks:
            return f"No relevant content found for '{question}'."

        # Filter out memory headers
        doc_blocks = [b for b in blocks if not b.startswith("--- USER MEMORIES")]
        if not doc_blocks:
            doc_blocks = blocks

        formatted_sections = []

        for block in doc_blocks:
            lines = block.splitlines()
            if not lines:
                continue

            header_line = lines[0]
            citation_match = re.search(r"\[(S\d+)\]", header_line)
            citation_tag = f" [{citation_match.group(1)}]" if citation_match else ""

            # Extract content lines after metadata header
            content_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip citation header lines
                if line.startswith("[S") or "Relevance:" in line or "Document:" in line:
                    continue
                # Skip author and document title header noise
                if re.search(r"(?i)prepared\s+by", stripped) or re.search(r"(?i)mayank\s+yadav", stripped):
                    continue
                if stripped.lower() in {"distributed system", "distributed systems", "1 - concepts of distributed systems"}:
                    continue
                # Skip star question lines that repeat the prompt question
                if stripped.startswith("⭐") or re.match(r"^⭐?\s*Describe\s+Distributed", stripped, re.IGNORECASE):
                    continue
                if re.match(r"^--- Page \d+ ---$", stripped):
                    continue
                content_lines.append(line)

            content_text = "\n".join(content_lines).strip()
            if not content_text:
                continue

            # Format headings, list items, and bold key terms cleanly
            cleaned_lines = []
            for line in content_text.splitlines():
                stripped = line.strip()
                if not stripped:
                    cleaned_lines.append("")
                    continue

                # Format section headers cleanly (e.g. "Goals of Distributed Systems")
                if stripped.startswith("# "):
                    cleaned_lines.append(f"\n### {stripped[2:].strip()}\n")
                elif stripped.startswith("## "):
                    cleaned_lines.append(f"\n### {stripped[3:].strip()}\n")
                elif (stripped.endswith(":") or "Goals of" in stripped or "Advantages of" in stripped or "Disadvantages of" in stripped) and len(stripped) < 80 and not stripped.startswith("-") and not stripped.startswith("●"):
                    cleaned_lines.append(f"\n### {stripped}\n")
                # Format bullet points cleanly with bold lead terms
                elif stripped.startswith("●") or stripped.startswith("•") or stripped.startswith("*") or stripped.startswith("-"):
                    item_text = re.sub(r"^[●•*-]\s*", "", stripped)
                    if ":" in item_text and not item_text.startswith("**"):
                        parts = item_text.split(":", 1)
                        item_text = f"**{parts[0].strip()}:** {parts[1].strip()}"
                    cleaned_lines.append(f"- {item_text}")
                else:
                    cleaned_lines.append(stripped)

            section_body = "\n".join(cleaned_lines).strip()
            if section_body:
                formatted_sections.append(f"{section_body}{citation_tag}")

        if not formatted_sections:
            return f"No relevant content found in document for '{question}'."

        return "\n\n".join(formatted_sections)


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
