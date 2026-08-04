export type SearchResult = {
  chunk_id: number;
  chunk_index: number;
  content: string;
  document_id: number;
  document_title: string;
  file_type?: string;
  similarity_score: number;
  relevance_score?: number;
  metadata?: {
    page_number?: number;
    unit_count?: number;
  };
};

export type SearchRequest = {
  query: string;
  limit?: number;
  min_score?: number;
  file_type?: string;
  document_id?: number;
};
