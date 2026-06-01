from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.services.retrieval import search_document_chunks

from .models import Conversation, Message
from .serializers import ChatRequestSerializer, ChatResponseSerializer


class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = ChatRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        message = request_serializer.validated_data["message"]
        conversation_id = request_serializer.validated_data.get("conversation_id")

        if conversation_id:
            conversation = get_object_or_404(
                Conversation.objects.filter(owner=request.user),
                pk=conversation_id,
            )
        else:
            conversation = Conversation.objects.create(
                owner=request.user,
                title=message[:80],
            )

        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=message,
        )

        chunks = search_document_chunks(request.user, message, limit=5)
        answer = (
            "Retrieval is working. LLM answer generation is intentionally not "
            "enabled until the knowledge pipeline is verified."
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=answer,
        )
        assistant_message.cited_chunks.set(chunks)
        user_message.cited_chunks.set([])

        sources = [
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

        response_serializer = ChatResponseSerializer(
            {
                "conversation_id": conversation.id,
                "answer": answer,
                "sources": sources,
            }
        )
        return Response(response_serializer.data)
