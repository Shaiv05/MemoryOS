"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Brain, Search } from "lucide-react";
import MemoryCard from "@/components/memory/MemoryCard";
import MemoryForm from "@/components/memory/MemoryForm";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import {
  createMemoryEntry,
  deleteMemoryEntry,
  getMemoryEntries,
  updateMemoryEntry,
} from "@/services/memory";
import { getApiErrorMessage } from "@/services/search";
import type { MemoryCategory, MemoryEntry, MemoryEntryInput } from "@/types/memory";

const categories: { value: MemoryCategory | ""; label: string }[] = [
  { value: "", label: "All" },
  { value: "fact", label: "Facts" },
  { value: "preference", label: "Preferences" },
  { value: "summary", label: "Summaries" },
  { value: "note", label: "Notes" },
  { value: "pinned", label: "Pinned" },
];

export default function MemoryPage() {
  const { token } = useAuth({ required: true });
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<MemoryCategory | "">("");
  const [editingMemory, setEditingMemory] = useState<MemoryEntry | null>(null);
  const [formVersion, setFormVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    let ignore = false;
    getMemoryEntries({ query, category })
      .then((data) => {
        if (!ignore) setMemories(data);
      })
      .catch((err: unknown) => {
        if (!ignore) setError(getApiErrorMessage(err, "Could not load memories."));
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [token, query, category]);

  const refreshMemories = async () => {
    const data = await getMemoryEntries({ query, category });
    setMemories(data);
  };

  const handleSubmit = async (input: MemoryEntryInput) => {
    setSaving(true);
    setError("");

    try {
      if (editingMemory) {
        await updateMemoryEntry(editingMemory.id, input);
      } else {
        await createMemoryEntry(input);
      }
      setEditingMemory(null);
      setFormVersion((current) => current + 1);
      await refreshMemories();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Could not save memory."));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    setError("");
    try {
      await deleteMemoryEntry(id);
      setMemories((current) => current.filter((memory) => memory.id !== id));
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Could not delete memory."));
    }
  };

  const handleTogglePin = async (id: number, current: boolean) => {
    try {
      await updateMemoryEntry(id, { is_pinned: !current });
      await refreshMemories();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Could not update pin status."));
    }
  };

  const handleQueryChange = (value: string) => {
    setLoading(true);
    setQuery(value);
  };

  const handleCategoryChange = (value: MemoryCategory | "") => {
    setLoading(true);
    setCategory(value);
  };

  const cancelEdit = () => {
    setEditingMemory(null);
    setFormVersion((current) => current + 1);
  };

  if (!token) return null;

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-6 md:p-10">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-6xl"
        >
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="flex items-center gap-3">
                <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-3">
                  <Brain className="h-5 w-5 text-emerald-400" />
                </div>
                <h1 className="text-4xl font-semibold tracking-tight">Memory</h1>
              </div>
              <p className="mt-3 max-w-2xl text-zinc-400">
                Store durable facts, preferences, summaries, and pinned knowledge.
              </p>
            </div>
          </div>

          <div className="mt-10 grid gap-8 lg:grid-cols-[420px_1fr]">
            <div className="space-y-5">
              <MemoryForm
                key={`${editingMemory?.id ?? "new"}-${formVersion}`}
                editingMemory={editingMemory}
                saving={saving}
                onCancel={cancelEdit}
                onSubmit={handleSubmit}
              />

              {error && (
                <p className="rounded border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">
                  {error}
                </p>
              )}
            </div>

            <section>
              <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
                <div className="flex flex-col gap-4 md:flex-row">
                  <div className="flex min-w-0 flex-1 items-center gap-3 rounded-lg bg-black border border-zinc-800 px-4 focus-within:border-zinc-600 transition">
                    <Search className="h-4 w-4 text-zinc-500" />
                    <input
                      value={query}
                      onChange={(event) => handleQueryChange(event.target.value)}
                      className="min-h-12 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
                      placeholder="Search memories by title, content, or #tags"
                    />
                  </div>
                  <select
                    value={category}
                    onChange={(event) =>
                      handleCategoryChange(event.target.value as MemoryCategory | "")
                    }
                    className="rounded-lg border border-zinc-800 bg-black px-4 py-3 text-sm text-white outline-none focus:border-zinc-600 transition"
                  >
                    {categories.map((item) => (
                      <option key={item.value || "all"} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-6">
                {loading ? (
                  <div className="grid gap-4">
                    {[0, 1, 2].map((item) => (
                      <div
                        key={item}
                        className="h-44 animate-pulse rounded-xl border border-zinc-800 bg-zinc-950"
                      />
                    ))}
                  </div>
                ) : memories.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 bg-zinc-950 p-12 text-zinc-500">
                    <p>No memories match the current filters.</p>
                  </div>
                ) : (
                  <div className="grid gap-4">
                    <AnimatePresence>
                      {memories.map((memory) => (
                        <MemoryCard
                          key={memory.id}
                          memory={memory}
                          onEdit={setEditingMemory}
                          onDelete={handleDelete}
                          onTogglePin={handleTogglePin}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            </section>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
