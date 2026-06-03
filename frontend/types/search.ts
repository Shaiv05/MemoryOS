export type SearchResult = {
  chunk_id: number;
  chunk_index: number;
  content: string;
  document_id: number;
  document_title: string;
  similarity_score: number;
};

export type SearchRequest = {
  query: string;
  limit?: number;
};
