export type ProcessingStatus = "queued" | "processing" | "completed" | "failed" | "pending";

export type Document = {
  id: number;
  title: string;
  file: string | null;
  file_type: "pdf" | "txt" | "docx" | "md" | "image" | "link" | "note";
  source_url: string | null;
  raw_text_preview: string;
  processing_status: ProcessingStatus;
  processing_error: string;
  extracted_at: string | null;
  chunk_count: number;
  file_size: number | null;
  page_count: number | null;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  processing_duration: number | null;
  created_at: string;
  updated_at: string;
};

export type CreateDocumentInput = {
  title: string;
  fileType: "pdf" | "txt" | "docx" | "md" | "image" | "link" | "note";
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
