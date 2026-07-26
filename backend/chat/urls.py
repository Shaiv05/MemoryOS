from django.urls import path

from .views import (
    ChatMessageView,
    ConversationClearView,
    ConversationDetailView,
    ConversationListView,
    ConversationRegenerateView,
)


urlpatterns = [
    path("message/", ChatMessageView.as_view(), name="chat-message"),
    path("conversations/", ConversationListView.as_view(), name="chat-conversation-list"),
    path(
        "conversations/<int:pk>/",
        ConversationDetailView.as_view(),
        name="chat-conversation-detail",
    ),
    path(
        "conversations/<int:pk>/clear/",
        ConversationClearView.as_view(),
        name="chat-conversation-clear",
    ),
    path(
        "conversations/<int:pk>/regenerate/",
        ConversationRegenerateView.as_view(),
        name="chat-conversation-regenerate",
    ),
]
