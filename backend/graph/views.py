from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Node, Edge
from .serializers import NodeSerializer, EdgeSerializer, GraphSerializer


class GraphDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nodes = Node.objects.filter(owner=request.user).prefetch_related("source_documents", "source_documents__notes")
        edges = Edge.objects.filter(owner=request.user).select_related("source", "target")

        serializer = GraphSerializer({
            "nodes": nodes,
            "edges": edges
        })
        return Response(serializer.data)


class NodeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            node = Node.objects.prefetch_related("source_documents", "source_documents__notes").get(
                owner=request.user, pk=pk
            )
            serializer = NodeSerializer(node)
            return Response(serializer.data)
        except Node.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
