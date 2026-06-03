from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ConversationDetailSerializer,
    ConversationSerializer,
)
from .services import chat_with_documents


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
            .prefetch_related("messages__cited_chunks__document"),
            pk=pk,
        )
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)

    def delete(self, request, pk):
        conversation = self.get_object(request, pk)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
