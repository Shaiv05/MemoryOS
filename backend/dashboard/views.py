from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentChunk


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
                "failed_documents": documents.filter(
                    processing_status=Document.PROCESSING_FAILED
                ).count(),
                "chunks": DocumentChunk.objects.filter(
                    document__owner=request.user
                ).count(),
            }
        )
