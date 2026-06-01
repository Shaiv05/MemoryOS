import api from "./api";
import type { ChatResponse } from "@/types/chat";

export const sendChatMessage = async (message: string, conversationId?: number) => {
  const res = await api.post<ChatResponse>("/chat/message/", {
    message,
    conversation_id: conversationId,
  });
  return res.data;
};
