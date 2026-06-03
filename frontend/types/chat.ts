export type ChatSource = {
  document_id: number;
  document_title: string;
  chunk_id: number;
  chunk_index: number;
  content: string;
  score: number;
  similarity_score: number;
};

export type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[];
  created_at: string;
};

export type ChatConversation = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatConversationDetail = ChatConversation & {
  messages: ChatMessage[];
};

export type ChatResponse = {
  conversation_id: number;
  message_id: number;
  answer: string;
  sources: ChatSource[];
};
