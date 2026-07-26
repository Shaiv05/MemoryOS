import json
import logging
import os

from django.db import transaction
from django.shortcuts import get_object_or_404

from documents.services.retrieval import retrieve_document_chunks
from memory.services import create_memory_entry

from .context import ContextBuilder, build_history_context, truncate_text
from .models import Conversation, Message, MessageSource
from .providers import get_ai_provider

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHUNKS = 5
MAX_HISTORY_MESSAGES = 8


def get_owned_conversation(user, conversation_id):
    return get_object_or_404(
        Conversation.objects.filter(owner=user),
        pk=conversation_id,
    )


def create_conversation(user, title=""):
    return Conversation.objects.create(owner=user, title=(title or "New chat")[:255])


def get_or_create_conversation(user, message, conversation_id=None):
    if conversation_id:
        return get_owned_conversation(user, conversation_id)
    return create_conversation(user, message[:80])


def get_recent_history(conversation):
    return list(conversation.messages.order_by("-created_at")[:MAX_HISTORY_MESSAGES])[::-1]


def source_to_dict(source):
    return {
        "document_id": source.document_id,
        "document_title": source.document.title,
        "chunk_id": source.document_chunk_id,
        "chunk_index": source.document_chunk.chunk_index,
        "page_number": source.page_number,
        "content": source.preview,
        "preview": source.preview,
        "score": source.relevance_score,
        "similarity_score": source.relevance_score,
        "relevance_score": source.relevance_score,
    }


def serialize_message_sources(message):
    persisted_sources = list(
        message.sources.select_related("document", "document_chunk").all()
    )
    if persisted_sources:
        return [source_to_dict(source) for source in persisted_sources]

    return serialize_chunk_sources(message.cited_chunks.select_related("document").all())


def serialize_chunk_sources(chunks):
    sources = []
    for chunk in chunks:
        distance = getattr(chunk, "score", None)
        relevance_score = max(0.0, min(1.0, 1.0 - float(distance))) if distance is not None else 0.0
        page_number = None
        metadata = chunk.metadata or {}
        if metadata.get("page_number") or metadata.get("page"):
            try:
                page_number = int(metadata.get("page_number") or metadata.get("page"))
            except (TypeError, ValueError):
                page_number = None
        sources.append(
            {
                "document_id": chunk.document_id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page_number": page_number,
                "content": truncate_text(chunk.content, 1800),
                "preview": truncate_text(chunk.content, 1800),
                "score": relevance_score,
                "similarity_score": relevance_score,
                "relevance_score": relevance_score,
            }
        )
    return sources


def persist_sources(message, context_sources):
    source_models = []
    chunk_ids = []
    for source in context_sources:
        chunk_ids.append(source.chunk_id)
        source_models.append(
            MessageSource(
                message=message,
                document_id=source.document_id,
                document_chunk_id=source.chunk_id,
                page_number=source.page_number,
                relevance_score=source.relevance_score,
                preview=truncate_text(source.content, 1800),
            )
        )
    if source_models:
        MessageSource.objects.bulk_create(source_models, ignore_conflicts=True)
        message.cited_chunks.set(chunk_ids)
    else:
        message.cited_chunks.clear()


@transaction.atomic
def chat_with_documents(user, message, conversation_id=None):
    conversation = get_or_create_conversation(user, message, conversation_id)
    history = get_recent_history(conversation)

    user_message = Message.objects.create(
        conversation=conversation,
        role="user",
        content=message,
    )

    return generate_assistant_response(user, conversation, user_message, history)


def generate_assistant_response(user, conversation, user_message, history):
    from memory.models import MemoryEntry
    retrieval_results = retrieve_document_chunks(user, user_message.content, limit=MAX_CONTEXT_CHUNKS)
    user_memories = list(MemoryEntry.objects.filter(owner=user).order_by("-is_pinned", "-updated_at")[:5])
    built_context = ContextBuilder().build(retrieval_results, memories=user_memories)
    history_context = build_history_context(history)
    provider = get_ai_provider()
    answer = provider.generate_response(
        question=user_message.content,
        context=built_context.prompt_context,
        history=history_context,
    )
    if not answer:
        answer = provider.generate_response(
            question=user_message.content,
            context=built_context.prompt_context,
            history="",
        )

    assistant_message = Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=answer,
    )
    persist_sources(assistant_message, built_context.sources)
    conversation.save(update_fields=["updated_at"])

    try:
        extract_memory_from_exchange(user, user_message.content, answer)
    except Exception as exc:
        logger.warning("Autonomous memory extraction failed: %s", exc)

    return {
        "conversation_id": conversation.id,
        "user_message_id": user_message.id,
        "message_id": assistant_message.id,
        "answer": answer,
        "sources": serialize_message_sources(assistant_message),
    }


@transaction.atomic
def regenerate_last_response(user, conversation_id):
    conversation = get_owned_conversation(user, conversation_id)
    last_user_message = (
        conversation.messages.filter(role="user").order_by("-created_at").first()
    )
    if not last_user_message:
        raise ValueError("Conversation has no user message to regenerate.")

    conversation.messages.filter(
        role="assistant",
        created_at__gt=last_user_message.created_at,
    ).delete()
    history = list(
        conversation.messages.filter(created_at__lt=last_user_message.created_at)
        .order_by("-created_at")[:MAX_HISTORY_MESSAGES]
    )[::-1]
    return generate_assistant_response(user, conversation, last_user_message, history)


def rename_conversation(user, conversation_id, title):
    conversation = get_owned_conversation(user, conversation_id)
    conversation.title = title[:255]
    conversation.save(update_fields=["title", "updated_at"])
    return conversation


def clear_conversation(user, conversation_id):
    conversation = get_owned_conversation(user, conversation_id)
    conversation.messages.all().delete()
    conversation.save(update_fields=["updated_at"])
    return conversation


def extract_memory_from_exchange(user, question, answer):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = (
        "You are a memory assistant. Based on this exchange, identify if there is any "
        "new long-term fact or preference about the user that should be remembered. "
        "If so, return a JSON object with 'title', 'content', 'category' "
        "(fact, preference, note). If nothing significant is found, return {}.\n\n"
        f"User: {question}\nAI: {answer}"
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    data = json.loads(response.choices[0].message.content)
    if data and "title" in data and "content" in data:
        create_memory_entry(
            user,
            {
                "title": data["title"],
                "content": data["content"],
                "category": data.get("category", "note"),
                "source": "autonomous",
            },
        )
