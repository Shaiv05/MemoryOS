import os
from openai import OpenAI
from documents.models import Document
from memory.models import MemoryEntry

def generate_ai_summary(user):
    """
    Generates a daily summary reasoning across user documents and memories.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Configure your OpenAI API key to enable AI summaries."

    # Fetch recent context
    recent_docs = Document.objects.filter(owner=user).order_by("-updated_at")[:5]
    recent_memories = MemoryEntry.objects.filter(owner=user).order_by("-updated_at")[:5]

    doc_titles = ", ".join([d.title for d in recent_docs])
    memory_titles = ", ".join([m.title for m in recent_memories])

    prompt = (
        "You are MemoryOS, the user's AI Second Brain. Generate a brief, professional daily summary "
        "of their current focus based on their recent documents and memories. "
        "Provide insights on what they are working on and suggest 1-2 next steps or connections they might have missed.\n\n"
        f"Recent Documents: {doc_titles}\n"
        f"Recent Memories: {memory_titles}\n\n"
        "Keep the summary under 150 words and maintain a premium, helpful tone."
    )

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate summary at this time: {str(e)}"
