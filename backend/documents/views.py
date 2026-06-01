from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import documents_for_user
from .serializers import DocumentSearchResultSerializer, DocumentSerializer
from .services.processing import process_document
from .services.retrieval import search_document_chunks


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return documents_for_user(self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        document = serializer.save(owner=self.request.user)
        process_document(document)


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return documents_for_user(self.request.user)


class DocumentProcessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        document = get_object_or_404(documents_for_user(request.user), pk=pk)
        process_document(document)
        serializer = DocumentSerializer(document, context={"request": request})
        return Response(serializer.data)


class DocumentSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        try:
            limit = min(int(request.query_params.get("limit", 5)), 20)
        except ValueError:
            return Response(
                {"detail": "limit must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        chunks = search_document_chunks(request.user, query, limit=limit)
        results = [
            {
                "document_id": chunk.document_id,
                "document_title": chunk.document.title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": float(chunk.score),
            }
            for chunk in chunks
        ]
        serializer = DocumentSearchResultSerializer(results, many=True)
        return Response(serializer.data)
