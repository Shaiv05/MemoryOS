import type { DocumentSearchResult } from "@/types/document";

export type ChatResponse = {
  conversation_id: number;
  answer: string;
  sources: DocumentSearchResult[];
};
