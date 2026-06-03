import api from "./api";
import type { SearchRequest, SearchResult } from "@/types/search";

export const getApiErrorMessage = (error: unknown, fallback: string) => {
  const response = (
    error as {
      response?: {
        data?: {
          detail?: string;
          query?: string[];
          limit?: string[];
          non_field_errors?: string[];
        };
      };
    }
  ).response;

  return (
    response?.data?.detail ||
    response?.data?.query?.[0] ||
    response?.data?.limit?.[0] ||
    response?.data?.non_field_errors?.[0] ||
    fallback
  );
};

export const searchDocuments = async ({ query, limit = 8 }: SearchRequest) => {
  const res = await api.post<SearchResult[]>("/search/", { query, limit });
  return res.data;
};
