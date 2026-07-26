from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .serializers import (
    ConversationCreateSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    ConversationDetailSerializer,
    ConversationRenameSerializer,
    ConversationSerializer,
)
from .services import (
    chat_with_documents,
    clear_conversation,
    create_conversation,
    regenerate_last_response,
    rename_conversation,
)


class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = ChatRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        message = request_serializer.validated_data["message"]
        conversation_id = request_serializer.validated_data.get("conversation_id")

        result = chat_with_documents(request.user, message, conversation_id)
        response_serializer = ChatResponseSerializer(result)
        return Response(response_serializer.data)


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(owner=request.user).order_by("-updated_at")
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request):
        request_serializer = ConversationCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        conversation = create_conversation(
            request.user,
            request_serializer.validated_data.get("title", ""),
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(
            Conversation.objects.filter(owner=request.user),
            pk=pk,
        )

    def get(self, request, pk):
        conversation = get_object_or_404(
            Conversation.objects.filter(owner=request.user)
            .prefetch_related(
                "messages__sources__document",
                "messages__sources__document_chunk",
                "messages__cited_chunks__document",
            ),
            pk=pk,
        )
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)

    def patch(self, request, pk):
        request_serializer = ConversationRenameSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        conversation = rename_conversation(
            request.user,
            pk,
            request_serializer.validated_data["title"],
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

    def delete(self, request, pk):
        conversation = self.get_object(request, pk)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationClearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        conversation = clear_conversation(request.user, pk)
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)


class ConversationRegenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            result = regenerate_last_response(request.user, pk)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = ChatResponseSerializer(result)
        return Response(response_serializer.data)
