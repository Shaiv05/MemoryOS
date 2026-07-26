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

export const createChatConversation = async (title?: string) => {
  const res = await api.post<ChatConversation>("/chat/conversations/", {
    title: title ?? "",
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

export const renameChatConversation = async (conversationId: number, title: string) => {
  const res = await api.patch<ChatConversation>(
    `/chat/conversations/${conversationId}/`,
    { title }
  );
  return res.data;
};

export const clearChatConversation = async (conversationId: number) => {
  const res = await api.post<ChatConversationDetail>(
    `/chat/conversations/${conversationId}/clear/`
  );
  return res.data;
};

export const regenerateChatResponse = async (conversationId: number) => {
  const res = await api.post<ChatResponse>(
    `/chat/conversations/${conversationId}/regenerate/`
  );
  return res.data;
};
