from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Node, Edge
from .serializers import NodeSerializer, EdgeSerializer, GraphSerializer


class GraphDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nodes = Node.objects.filter(owner=request.user)
        edges = Edge.objects.filter(owner=request.user)
        
        serializer = GraphSerializer({
            "nodes": nodes,
            "edges": edges
        })
        return Response(serializer.data)


class NodeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            node = Node.objects.get(owner=request.user, pk=pk)
            serializer = NodeSerializer(node)
            
            # Include related documents for context
            data = serializer.data
            data["source_documents"] = [
                {"id": doc.id, "title": doc.title}
                for doc in node.source_documents.all()
            ]
            return Response(data)
        except Node.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
