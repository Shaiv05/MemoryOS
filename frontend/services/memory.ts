import api from "./api";
import type { MemoryEntry, MemoryEntryInput, MemoryFilters } from "@/types/memory";

export const getMemoryEntries = async (filters: MemoryFilters = {}) => {
  const res = await api.get<MemoryEntry[]>("/memory/", {
    params: {
      q: filters.query || undefined,
      category: filters.category || undefined,
      pinned: filters.pinned,
    },
  });
  return res.data;
};

export const createMemoryEntry = async (input: MemoryEntryInput) => {
  const res = await api.post<MemoryEntry>("/memory/", input);
  return res.data;
};

export const updateMemoryEntry = async (id: number, input: Partial<MemoryEntryInput>) => {
  const res = await api.patch<MemoryEntry>(`/memory/${id}/`, input);
  return res.data;
};

export const deleteMemoryEntry = async (id: number) => {
  await api.delete(`/memory/${id}/`);
};
