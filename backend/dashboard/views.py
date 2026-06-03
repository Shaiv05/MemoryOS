from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentChunk
from memory.models import MemoryEntry
from productivity.models import Task
from .services import generate_ai_summary


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(owner=request.user)
        return Response(
            {
                "documents": documents.count(),
                "completed_documents": documents.filter(
                    processing_status=Document.PROCESSING_COMPLETED
                ).count(),
                "memories": MemoryEntry.objects.filter(owner=request.user).count(),
                "pending_tasks": Task.objects.filter(owner=request.user, status="pending").count(),
                "chunks": DocumentChunk.objects.filter(
                    document__owner=request.user
                ).count(),
            }
        )


class AiSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = generate_ai_summary(request.user)
        return Response({"summary": summary})
