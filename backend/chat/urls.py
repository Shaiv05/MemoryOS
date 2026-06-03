from django.urls import path

from .views import ChatMessageView, ConversationDetailView, ConversationListView


urlpatterns = [
    path("message/", ChatMessageView.as_view(), name="chat-message"),
    path("conversations/", ConversationListView.as_view(), name="chat-conversation-list"),
    path(
        "conversations/<int:pk>/",
        ConversationDetailView.as_view(),
        name="chat-conversation-detail",
    ),
]
