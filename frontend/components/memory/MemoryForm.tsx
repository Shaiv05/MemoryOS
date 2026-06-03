"use client";

import { FormEvent, useState } from "react";
import type { MemoryCategory, MemoryEntry, MemoryEntryInput } from "@/types/memory";

type MemoryFormProps = {
  editingMemory: MemoryEntry | null;
  saving: boolean;
  onCancel: () => void;
  onSubmit: (input: MemoryEntryInput) => void;
};

const categories: { value: MemoryCategory; label: string }[] = [
  { value: "fact", label: "Fact" },
  { value: "preference", label: "Preference" },
  { value: "summary", label: "Summary" },
  { value: "note", label: "Note" },
  { value: "pinned", label: "Pinned" },
];

export default function MemoryForm({
  editingMemory,
  saving,
  onCancel,
  onSubmit,
}: MemoryFormProps) {
  const [title, setTitle] = useState(editingMemory?.title ?? "");
  const [content, setContent] = useState(editingMemory?.content ?? "");
  const [category, setCategory] = useState<MemoryCategory>(
    editingMemory?.category ?? "note"
  );
  const [tags, setTags] = useState(editingMemory?.tags.join(", ") ?? "");
  const [isPinned, setIsPinned] = useState(editingMemory?.is_pinned ?? false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit({
      title: title.trim(),
      content: content.trim(),
      category,
      tags: tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      is_pinned: isPinned,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-zinc-800 bg-zinc-950 p-5"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="rounded border border-zinc-800 bg-black px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-zinc-600"
          placeholder="Memory title"
        />
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value as MemoryCategory)}
          className="rounded border border-zinc-800 bg-black px-4 py-3 text-sm text-white outline-none focus:border-zinc-600"
        >
          {categories.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      <textarea
        value={content}
        onChange={(event) => setContent(event.target.value)}
        className="mt-4 min-h-32 w-full resize-none rounded border border-zinc-800 bg-black px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-zinc-600"
        placeholder="Store the long-term fact, preference, summary, or note"
      />

      <div className="mt-4 grid gap-4 md:grid-cols-[1fr_auto]">
        <input
          value={tags}
          onChange={(event) => setTags(event.target.value)}
          className="rounded border border-zinc-800 bg-black px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-zinc-600"
          placeholder="Tags, comma separated"
        />
        <label className="flex items-center gap-3 rounded border border-zinc-800 bg-black px-4 py-3 text-sm text-zinc-300">
          <input
            type="checkbox"
            checked={isPinned}
            onChange={(event) => setIsPinned(event.target.checked)}
            className="h-4 w-4"
          />
          Pin
        </label>
      </div>

      <div className="mt-5 flex justify-end gap-3">
        {editingMemory && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded border border-zinc-800 px-4 py-2 text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={saving || !title.trim() || !content.trim()}
          className="rounded bg-white px-5 py-2 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? "Saving..." : editingMemory ? "Update memory" : "Create memory"}
        </button>
      </div>
    </form>
  );
}
