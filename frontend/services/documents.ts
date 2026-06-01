import api from "./api";
import type {
  CreateDocumentInput,
  Document,
  DocumentSearchResult,
} from "@/types/document";

export const getDocuments = async () => {
  const res = await api.get<Document[]>("/documents/");
  return res.data;
};

export const createDocument = async (input: CreateDocumentInput) => {
  if (input.file) {
    const formData = new FormData();
    formData.append("title", input.title);
    formData.append("file_type", input.fileType);
    formData.append("file", input.file);
    if (input.rawText) formData.append("raw_text", input.rawText);
    if (input.sourceUrl) formData.append("source_url", input.sourceUrl);

    const res = await api.post<Document>("/documents/", formData);
    return res.data;
  }

  const res = await api.post<Document>("/documents/", {
    title: input.title,
    file_type: input.fileType,
    raw_text: input.rawText ?? "",
    source_url: input.sourceUrl ?? "",
  });

  return res.data;
};

export const deleteDocument = async (id: number) => {
  return api.delete(`/documents/${id}/`);
};

export const reprocessDocument = async (id: number) => {
  const res = await api.post<Document>(`/documents/${id}/process/`);
  return res.data;
};

export const searchDocuments = async (query: string) => {
  const res = await api.get<DocumentSearchResult[]>("/documents/search/", {
    params: { q: query },
  });
  return res.data;
};
