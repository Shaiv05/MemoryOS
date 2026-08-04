from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.services.retrieval import search_document_chunks
from .serializers import SearchQuerySerializer, SearchResultSerializer


class SemanticSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy() if isinstance(request.data, dict) else {}

        if "query" not in data and "q" in data:
            data["query"] = data["q"]

        if "query" not in data or not data["query"]:
            data["query"] = request.query_params.get("query", request.query_params.get("q", ""))

        if "limit" not in data and request.query_params.get("limit"):
            data["limit"] = request.query_params.get("limit")

        if "file_type" not in data and request.query_params.get("file_type"):
            data["file_type"] = request.query_params.get("file_type")

        serializer = SearchQuerySerializer(data=data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        limit = serializer.validated_data.get("limit", 10)
        min_score = serializer.validated_data.get("min_score", 0.20)
        file_type = serializer.validated_data.get("file_type")
        document_id = serializer.validated_data.get("document_id")

        chunks = search_document_chunks(
            user=request.user,
            query=query,
            limit=limit,
            min_score=min_score,
            document_id=document_id,
            file_type=file_type,
        )
        result_serializer = SearchResultSerializer(chunks, many=True)
        return Response(result_serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        return self.post(request)
