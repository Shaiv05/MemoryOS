"use client";

import { useState } from "react";
import type { CreateDocumentInput } from "@/types/document";

type DocumentFormProps = {
  onSubmit: (input: CreateDocumentInput) => Promise<void>;
  loading: boolean;
};

export default function DocumentForm({ onSubmit, loading }: DocumentFormProps) {
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const fileType = file?.name.toLowerCase().endsWith(".txt") ? "txt" : "pdf";

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!title.trim() || (!file && !rawText.trim())) return;

    await onSubmit({
      title: title.trim(),
      fileType: file ? fileType : "note",
      rawText: file ? undefined : rawText,
      file,
    });

    setTitle("");
    setRawText("");
    setFile(null);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-8 rounded-lg border border-zinc-800 bg-zinc-950 p-6"
    >
      <input
        className="mb-4 w-full rounded bg-zinc-900 p-3 outline-none focus:ring-2 focus:ring-zinc-700"
        placeholder="Document title"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />

      <textarea
        className="mb-4 w-full rounded bg-zinc-900 p-3 outline-none focus:ring-2 focus:ring-zinc-700"
        placeholder="Write notes..."
        rows={5}
        value={rawText}
        onChange={(event) => setRawText(event.target.value)}
        disabled={Boolean(file)}
      />

      <input
        type="file"
        accept=".pdf,.txt,application/pdf,text/plain"
        onChange={(event) => setFile(event.target.files?.[0] || null)}
        className="mb-4 block text-sm text-zinc-300 file:mr-4 file:rounded file:border-0 file:bg-white file:px-3 file:py-2 file:text-sm file:font-medium file:text-black"
      />

      <button
        type="submit"
        disabled={loading}
        className="rounded bg-white px-4 py-2 font-medium text-black disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Saving..." : file ? "Upload Document" : "Save Note"}
      </button>
    </form>
  );
}
