import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, *, question: str, context: str, history: str) -> str:
        raise NotImplementedError


class LocalGroundedProvider(AIProvider):
    def generate_response(self, *, question: str, context: str, history: str) -> str:
        if not context:
            return (
                "I could not find relevant processed document context for this question. "
                "Upload or reprocess documents, then try again."
            )

        excerpts = []
        for block in context.split("\n\n")[:3]:
            label = block.split("]", 1)[0].replace("[", "")
            text = block.split("\n")[-1]
            excerpts.append(f"[{label}] {text[:700]}")

        return (
            f"Based on the retrieved document context for \"{question}\", the strongest "
            f"available evidence is below.\n\n" + "\n\n".join(excerpts)
        )


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_response(self, *, question: str, context: str, history: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are MemoryOS, a document-grounded assistant. Answer only from "
                        "the provided context. Cite sources inline with [S1], [S2], etc. "
                        "If the context is insufficient, say what is missing."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Conversation history:\n{history or 'No previous messages.'}\n\n"
                        f"Retrieved context:\n{context or 'No relevant context retrieved.'}\n\n"
                        f"User question:\n{question}"
                    ),
                },
            ],
            temperature=0.2,
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
            "AI_PROVIDER=openai but OPENAI_API_KEY is missing or empty; "
            "falling back to local grounded provider."
        )
        return LocalGroundedProvider()
    if provider_name not in {"local", "placeholder"}:
        logger.warning("AI_PROVIDER=%s is not configured; using local provider.", provider_name)
    return LocalGroundedProvider()
