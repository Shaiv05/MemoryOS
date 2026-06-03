import api from "./api";
import type {
  ChatConversation,
  ChatConversationDetail,
  ChatResponse,
} from "@/types/chat";

export const sendChatMessage = async (message: string, conversationId?: number) => {
  const res = await api.post<ChatResponse>("/chat/message/", {
    message,
    conversation_id: conversationId,
  });
  return res.data;
};

export const getChatConversations = async () => {
  const res = await api.get<ChatConversation[]>("/chat/conversations/");
  return res.data;
};

export const getChatConversation = async (conversationId: number) => {
  const res = await api.get<ChatConversationDetail>(
    `/chat/conversations/${conversationId}/`
  );
  return res.data;
};

export const deleteChatConversation = async (conversationId: number) => {
  await api.delete(`/chat/conversations/${conversationId}/`);
};
