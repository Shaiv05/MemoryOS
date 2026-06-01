export type ProcessingStatus = "pending" | "processing" | "completed" | "failed";

export type Document = {
  id: number;
  title: string;
  file: string | null;
  file_type: "pdf" | "txt" | "docx" | "link" | "note";
  source_url: string | null;
  raw_text_preview: string;
  processing_status: ProcessingStatus;
  processing_error: string;
  extracted_at: string | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
};

export type CreateDocumentInput = {
  title: string;
  fileType: "pdf" | "txt" | "link" | "note";
  rawText?: string;
  file?: File | null;
  sourceUrl?: string;
};

export type DocumentSearchResult = {
  document_id: number;
  document_title: string;
  chunk_id: number;
  chunk_index: number;
  content: string;
  score: number;
};
