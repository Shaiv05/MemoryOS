from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.services.search import search_document_chunks
from .serializers import SearchQuerySerializer, SearchResultSerializer


class SemanticSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract parameters from POST body or query parameters as fallback
        data = request.data.copy() if isinstance(request.data, dict) else {}
        
        if "query" not in data and "q" in data:
            data["query"] = data["q"]
            
        if "query" not in data or not data["query"]:
            data["query"] = request.query_params.get("query", request.query_params.get("q", ""))
            
        if "limit" not in data:
            data["limit"] = request.query_params.get("limit", 5)

        serializer = SearchQuerySerializer(data=data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        limit = serializer.validated_data["limit"]

        chunks = search_document_chunks(request.user, query, limit=limit)
        result_serializer = SearchResultSerializer(chunks, many=True)
        return Response(result_serializer.data, status=status.HTTP_200_OK)
