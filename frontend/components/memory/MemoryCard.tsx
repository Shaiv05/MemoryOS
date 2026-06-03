"use client";

import { motion } from "framer-motion";
import { Edit3, Pin, Trash2 } from "lucide-react";
import type { MemoryEntry } from "@/types/memory";

type MemoryCardProps = {
  memory: MemoryEntry;
  onEdit: (memory: MemoryEntry) => void;
  onDelete: (id: number) => void;
  onTogglePin?: (id: number, current: boolean) => void;
};

const categoryLabel: Record<MemoryEntry["category"], string> = {
  fact: "Fact",
  preference: "Preference",
  summary: "Summary",
  note: "Note",
  pinned: "Pinned",
};

export default function MemoryCard({
  memory,
  onEdit,
  onDelete,
  onTogglePin,
}: MemoryCardProps) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className={`rounded-xl border transition p-6 ${
        memory.is_pinned
          ? "border-amber-900/50 bg-amber-950/10 hover:border-amber-700/60"
          : "border-zinc-800 bg-zinc-950 hover:border-zinc-700 hover:bg-zinc-900/70"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-zinc-800 bg-black/40 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-zinc-500">
              {categoryLabel[memory.category]}
            </span>
            {memory.is_pinned && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-900/70 bg-amber-900/20 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">
                <Pin className="h-2.5 w-2.5 fill-current" />
                Pinned
              </span>
            )}
          </div>
          <h2 className="mt-4 text-xl font-semibold tracking-tight text-white">
            {memory.title}
          </h2>
        </div>

        <div className="flex shrink-0 gap-1.5">
          {onTogglePin && (
            <button
              onClick={() => onTogglePin(memory.id, memory.is_pinned)}
              className={`rounded-lg border p-2 transition ${
                memory.is_pinned
                  ? "border-amber-800/60 text-amber-400 bg-amber-950/30 hover:bg-amber-950/50"
                  : "border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300"
              }`}
              aria-label={memory.is_pinned ? "Unpin memory" : "Pin memory"}
            >
              <Pin className={`h-4 w-4 ${memory.is_pinned ? "fill-current" : ""}`} />
            </button>
          )}
          <button
            onClick={() => onEdit(memory)}
            className="rounded-lg border border-zinc-800 p-2 text-zinc-500 transition hover:border-zinc-600 hover:text-white"
            aria-label="Edit memory"
          >
            <Edit3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => onDelete(memory.id)}
            className="rounded-lg border border-zinc-800 p-2 text-zinc-500 transition hover:border-red-900 hover:text-red-400"
            aria-label="Delete memory"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed text-zinc-400">
        {memory.content}
      </p>

      {memory.tags.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {memory.tags.map((tag) => (
            <span
              key={`${memory.id}-${tag}`}
              className="rounded-md border border-zinc-800/50 bg-black/40 px-2 py-1 text-[10px] font-medium text-zinc-500 transition hover:border-zinc-700 hover:text-zinc-300"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </motion.article>
  );
}
