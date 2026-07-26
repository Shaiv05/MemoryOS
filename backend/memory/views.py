from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MemoryEntry
from .serializers import MemoryEntrySerializer
from .services import create_memory_entry, search_memory_entries, update_memory_entry


class MemoryEntryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get("category", "")
        query = request.query_params.get("q", "")
        pinned_param = request.query_params.get("pinned")
        pinned = None

        if pinned_param in {"true", "1"}:
            pinned = True
        elif pinned_param in {"false", "0"}:
            pinned = False

        queryset = search_memory_entries(
            request.user,
            query=query,
            category=category,
            pinned=pinned,
        )
        serializer = MemoryEntrySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MemoryEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        memory_entry = create_memory_entry(request.user, serializer.validated_data)
        return Response(
            MemoryEntrySerializer(memory_entry).data,
            status=status.HTTP_201_CREATED,
        )


class MemoryEntryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(MemoryEntry.objects.filter(owner=request.user), pk=pk)

    def get(self, request, pk):
        memory_entry = self.get_object(request, pk)
        return Response(MemoryEntrySerializer(memory_entry).data)

    def patch(self, request, pk):
        memory_entry = self.get_object(request, pk)
        serializer = MemoryEntrySerializer(
            memory_entry,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        memory_entry = update_memory_entry(memory_entry, serializer.validated_data)
        return Response(MemoryEntrySerializer(memory_entry).data)

    def delete(self, request, pk):
        memory_entry = self.get_object(request, pk)
        memory_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
