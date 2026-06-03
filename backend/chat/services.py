import os

from django.db import transaction
from django.shortcuts import get_object_or_404

from documents.services.retrieval import search_document_chunks

from .models import Conversation, Message


MAX_CONTEXT_CHUNKS = 5
MAX_HISTORY_MESSAGES = 8
MAX_CONTEXT_CHARS = 12000
MAX_HISTORY_CHARS = 4000
MAX_SOURCE_CHARS = 1800


def get_owned_conversation(user, conversation_id):
    return get_object_or_404(
        Conversation.objects.filter(owner=user),
        pk=conversation_id,
    )


def get_or_create_conversation(user, message, conversation_id=None):
    if conversation_id:
        return get_owned_conversation(user, conversation_id)

    return Conversation.objects.create(
        owner=user,
        title=message[:80],
    )


def similarity_from_distance(score):
    if score is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 - float(score)))


def serialize_chunk_sources(chunks):
    sources = []
    for chunk in chunks:
        distance = getattr(chunk, "score", None)
        similarity_score = similarity_from_distance(distance)
        sources.append(
            {
                "document_id": chunk.document_id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": truncate_text(chunk.content, MAX_SOURCE_CHARS),
                "score": similarity_score,
                "similarity_score": similarity_score,
            }
        )
    return sources


def truncate_text(value, max_chars):
    value = value or ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars].rsplit(' ', 1)[0]}..."


def get_recent_history(conversation):
    return list(conversation.messages.order_by("-created_at")[:MAX_HISTORY_MESSAGES])[::-1]


def assemble_context(chunks):
    if not chunks:
        return ""

    context_blocks = []
    for index, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            (
                f"[S{index}] Document: {chunk.document.title}\n"
                f"Chunk: {chunk.chunk_index}\n"
                f"{chunk.content}"
            )
        )
    return truncate_text("\n\n".join(context_blocks), MAX_CONTEXT_CHARS)


def build_prompt_messages(question, context, history):
    system_prompt = (
        "You are MemoryOS, a document-grounded assistant. Answer only from the "
        "provided context. Cite sources inline with [S1], [S2], etc. If the "
        "context is insufficient, say what is missing."
    )

    history_text = "\n".join(
        f"{message.role}: {message.content}" for message in history if message.content
    )
    history_text = truncate_text(history_text, MAX_HISTORY_CHARS)

    user_prompt = (
        f"Conversation history:\n{history_text or 'No previous messages.'}\n\n"
        f"Retrieved context:\n{context or 'No relevant context retrieved.'}\n\n"
        f"User question:\n{question}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def generate_fallback_answer(question, sources):
    if not sources:
        return (
            "I could not find relevant processed document chunks for this question. "
            "Upload or reprocess documents, then try again."
        )

    leading_sources = sources[:3]
    source_labels = ", ".join(f"[S{index}]" for index in range(1, len(leading_sources) + 1))
    excerpts = "\n\n".join(
        f"[S{index}] {source['document_title']}: {truncate_text(source['content'], 700)}"
        for index, source in enumerate(leading_sources, start=1)
    )
    return (
        f"Based on the retrieved document context for \"{question}\", the most "
        f"relevant evidence is in {source_labels}.\n\n{excerpts}"
    )


def generate_ai_answer(question, sources, history):
    context = assemble_context_for_sources(sources)
    messages = build_prompt_messages(question, context, history)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return generate_fallback_answer(question, sources)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.2,
        )
        answer = response.choices[0].message.content
        return answer or generate_fallback_answer(question, sources)
    except Exception:
        return generate_fallback_answer(question, sources)


def assemble_context_for_sources(sources):
    if not sources:
        return ""
    return truncate_text("\n\n".join(
        (
            f"[S{index}] Document: {source['document_title']}\n"
            f"Chunk: {source['chunk_index']}\n"
            f"{source['content']}"
        )
        for index, source in enumerate(sources, start=1)
    ), MAX_CONTEXT_CHARS)


from memory.services import create_memory_entry

@transaction.atomic
def chat_with_documents(user, message, conversation_id=None):
    conversation = get_or_create_conversation(user, message, conversation_id)
    history = get_recent_history(conversation)

    user_message = Message.objects.create(
        conversation=conversation,
        role="user",
        content=message,
    )

    chunks = search_document_chunks(user, message, limit=MAX_CONTEXT_CHUNKS)
    sources = serialize_chunk_sources(chunks)
    answer = generate_ai_answer(message, sources, history)

    assistant_message = Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=answer,
    )
    assistant_message.cited_chunks.set(chunks)
    user_message.cited_chunks.clear()
    conversation.save(update_fields=["updated_at"])
    
    # Phase 10: Autonomous Memory Extraction
    try:
        extract_memory_from_exchange(user, message, answer)
    except Exception as e:
        print(f"Autonomous memory extraction failed: {e}")

    return {
        "conversation_id": conversation.id,
        "message_id": assistant_message.id,
        "answer": answer,
        "sources": sources,
    }


def extract_memory_from_exchange(user, question, answer):
    """
    Uses AI to determine if a new fact or preference should be added to memory.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return

    client = OpenAI(api_key=api_key)
    
    prompt = (
        "You are a memory assistant. Based on this exchange, identify if there is any new long-term fact or preference "
        "about the user that should be remembered. If so, return a JSON object with 'title', 'content', 'category' (fact, preference, note). "
        "If nothing significant is found, return an empty JSON object {}.\n\n"
        f"User: {question}\nAI: {answer}"
    )
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        data = json.loads(response.choices[0].message.content)
        if data and "title" in data and "content" in data:
            create_memory_entry(user, {
                "title": data["title"],
                "content": data["content"],
                "category": data.get("category", "note"),
                "source": "autonomous"
            })
    except Exception:
        pass
