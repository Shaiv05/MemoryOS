"use client";

import type { Document } from "@/types/document";

const statusClass: Record<Document["processing_status"], string> = {
  pending: "border-zinc-700 text-zinc-300",
  processing: "border-blue-900 text-blue-300",
  completed: "border-emerald-900 text-emerald-300",
  failed: "border-red-900 text-red-300",
};

type DocumentCardProps = {
  document: Document;
  onDelete: (id: number) => Promise<void>;
  onReprocess: (id: number) => Promise<void>;
};

export default function DocumentCard({
  document,
  onDelete,
  onReprocess,
}: DocumentCardProps) {
  return (
    <article className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold">{document.title}</h2>
          <p className="mt-1 text-sm text-zinc-500">
            {document.file_type.toUpperCase()} · {document.chunk_count} chunks
          </p>
        </div>

        <span
          className={`rounded-full border px-3 py-1 text-xs uppercase ${statusClass[document.processing_status]}`}
        >
          {document.processing_status}
        </span>
      </div>

      {document.raw_text_preview && (
        <p className="mt-4 line-clamp-4 text-sm leading-6 text-zinc-400">
          {document.raw_text_preview}
        </p>
      )}

      {document.processing_error && (
        <p className="mt-4 rounded border border-red-900/60 bg-red-950/50 p-3 text-sm text-red-300">
          {document.processing_error}
        </p>
      )}

      <div className="mt-4 flex gap-3">
        <button
          onClick={() => onReprocess(document.id)}
          className="rounded border border-zinc-700 px-3 py-1 text-sm text-zinc-200 hover:bg-zinc-900"
        >
          Reprocess
        </button>
        <button
          onClick={() => onDelete(document.id)}
          className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-500"
        >
          Delete
        </button>
      </div>
    </article>
  );
}
