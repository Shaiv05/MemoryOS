import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from chat.services import chat_with_documents
from documents.models import Document
from documents.services.document_processor import process_document
from memory.models import MemoryEntry
from productivity.models import Goal, Note, Task


class Command(BaseCommand):
    help = "Create a demo superuser and sample content when the database is empty."

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.exists():
            self.stdout.write("Database already has users; skipping demo seed.")
            return

        username = os.getenv("DEMO_SUPERUSER_USERNAME", "demo")
        email = os.getenv("DEMO_SUPERUSER_EMAIL", "demo@memoryos.local")
        password = os.getenv("DEMO_SUPERUSER_PASSWORD", "demo12345")

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created demo superuser: {username}"))

        doc_specs = [
            {
                "title": "MemoryOS Product Overview",
                "raw_text": (
                    "MemoryOS is a personal knowledge and productivity operating system. "
                    "It ingests documents such as PDF, TXT, and DOCX files, chunks them, "
                    "and stores vector embeddings in PostgreSQL with pgvector. Users can chat "
                    "with their documents using retrieval-augmented generation and see cited "
                    "sources. The knowledge graph extracts entities like people, projects, and "
                    "technologies, linking them across documents."
                ),
            },
            {
                "title": "Demo Meeting Notes",
                "raw_text": (
                    "Project MemoryOS demo preparation: finalize Docker setup, verify chat "
                    "with OpenAI provider, upload sample documents, and review the knowledge "
                    "graph view. Shaiv owns the presentation deck. The team uses Django, "
                    "Next.js, PostgreSQL, and OpenAI GPT models."
                ),
            },
        ]

        documents = []
        for spec in doc_specs:
            document = Document.objects.create(
                owner=user,
                title=spec["title"],
                file_type="note",
                raw_text=spec["raw_text"],
            )
            try:
                process_document(document)
            except Exception as exc:  # pragma: no cover - resilient demo seeding
                self.stdout.write(self.style.WARNING(f"  Processing skipped for {document.title}: {exc}"))
            documents.append(document)
            self.stdout.write(f"  Seeded document: {document.title}")

        self._seed_goals(user)

        Note.objects.create(
            owner=user,
            title="Demo checklist",
            content=(
                "1. Register or log in as demo user.\n"
                "2. Upload a document and wait for processing.\n"
                "3. Ask a question in chat and verify citations.\n"
                "4. Open the knowledge graph to explore entities."
            ),
        )
        Task.objects.create(
            owner=user,
            title="Prepare live demo",
            description="Walk through register, upload, chat, and graph flow.",
            status="in_progress",
            priority="high",
        )
        Task.objects.create(
            owner=user,
            title="Review seeded documents",
            description="Confirm embeddings and graph nodes were created.",
            status="pending",
            priority="medium",
        )
        MemoryEntry.objects.create(
            owner=user,
            title="Preferred AI provider",
            content="Use OpenAI for grounded chat when OPENAI_API_KEY is configured.",
            category=MemoryEntry.CATEGORY_PREFERENCE,
            tags=["demo", "ai"],
        )

        try:
            chat_with_documents(
                user,
                "Summarize the MemoryOS demo themes and point me to the most relevant documents.",
            )
            MemoryEntry.objects.create(
                owner=user,
                title="Demo chat memory",
                content="The demo conversation should highlight retrieval, citations, and the knowledge graph workflow.",
                category=MemoryEntry.CATEGORY_NOTE,
                tags=["demo", "chat", "memory"],
                source="seed_demo",
            )
        except Exception as exc:  # pragma: no cover - resilient demo seeding
            self.stdout.write(self.style.WARNING(f"  Demo conversation skipped: {exc}"))

        if documents:
            note = Note.objects.get(owner=user, title="Demo checklist")
            note.related_documents.set(documents[:1])

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))

    def _seed_goals(self, user):
        goal_specs = [
            {
                "title": "Learn Machine Learning",
                "description": "Complete a focused study plan for neural networks, embeddings, and retrieval systems.",
                "progress": 40,
                "status": "in_progress",
                "priority": "high",
                "deadline": date(2026, 9, 15),
            },
            {
                "title": "Complete MemoryOS MVP",
                "description": "Polish the document ingestion, chat, and graph experiences for the investor demo.",
                "progress": 70,
                "status": "in_progress",
                "priority": "high",
                "deadline": date(2026, 8, 1),
            },
            {
                "title": "Finish Semester Project",
                "description": "Deliver the final write-up and validation for the AI assistant prototype.",
                "progress": 65,
                "status": "in_progress",
                "priority": "medium",
                "deadline": date(2026, 7, 28),
            },
            {
                "title": "Prepare Presentation",
                "description": "Create a concise deck that demonstrates RAG, memory extraction, and graph navigation.",
                "progress": 55,
                "status": "planned",
                "priority": "medium",
                "deadline": date(2026, 7, 30),
            },
            {
                "title": "Build AI Portfolio",
                "description": "Publish the MemoryOS demo walkthrough, architecture notes, and screenshots for recruiters.",
                "progress": 35,
                "status": "planned",
                "priority": "high",
                "deadline": date(2026, 10, 1),
            },
            {
                "title": "Apply for Internship",
                "description": "Submit tailored applications to AI and product teams while sharing the project demo link.",
                "progress": 20,
                "status": "planned",
                "priority": "medium",
                "deadline": date(2026, 8, 15),
            },
        ]

        for spec in goal_specs:
            Goal.objects.create(
                owner=user,
                title=spec["title"],
                description=spec["description"],
                status=spec["status"],
                priority=spec["priority"],
                target_date=spec["deadline"],
                progress=spec["progress"],
                is_completed=spec["progress"] >= 100,
            )
