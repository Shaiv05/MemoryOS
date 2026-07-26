export type MemoryCategory = "fact" | "preference" | "summary" | "note" | "pinned";

export type MemoryEntry = {
  id: number;
  title: string;
  content: string;
  category: MemoryCategory;
  tags: string[];
  is_pinned: boolean;
  source: string;
  created_at: string;
  updated_at: string;
};

export type MemoryEntryInput = {
  title: string;
  content: string;
  category: MemoryCategory;
  tags: string[];
  is_pinned: boolean;
};

export type MemoryFilters = {
  query?: string;
  category?: MemoryCategory | "";
  pinned?: boolean;
};
