"use client";

import { useState } from "react";
import type { Document } from "@/types/document";
import { Clock, FileText, Layers, HardDrive, RefreshCw, Trash2, ShieldAlert } from "lucide-react";

const statusClass: Record<Document["processing_status"], string> = {
  queued: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  pending: "border-zinc-700 bg-zinc-800/30 text-zinc-300",
  processing: "border-blue-500/40 bg-blue-500/10 text-blue-400 animate-pulse",
  completed: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  failed: "border-red-500/30 bg-red-500/10 text-red-400",
};

type DocumentCardProps = {
  document: Document;
  onDelete: (id: number) => Promise<void>;
  onReprocess: (id: number) => Promise<void>;
};

function formatBytes(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return "N/A";
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

export default function DocumentCard({
  document,
  onDelete,
  onReprocess,
}: DocumentCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isReprocessing, setIsReprocessing] = useState(false);

  const handleDelete = async () => {
    if (confirm(`Are you sure you want to delete "${document.title}"?`)) {
      setIsDeleting(true);
      try {
        await onDelete(document.id);
      } catch {
        setIsDeleting(false);
      }
    }
  };

  const handleReprocess = async () => {
    setIsReprocessing(true);
    try {
      await onReprocess(document.id);
    } finally {
      setIsReprocessing(false);
    }
  };

  const isWorking = document.processing_status === "processing" || document.processing_status === "queued" || isReprocessing;

  return (
    <article className="group relative rounded-xl border border-zinc-800/80 bg-zinc-950/40 p-5 backdrop-blur-md transition-all duration-300 hover:border-zinc-700/80 hover:bg-zinc-900/20">

      {/* Top row */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="mt-1 rounded-lg bg-zinc-900 p-2 text-zinc-400 group-hover:text-white transition-colors duration-300">
            <FileText size={18} />
          </div>
          <div>
            <h2 className="text-base font-bold text-zinc-100 group-hover:text-white">{document.title}</h2>
            <p className="text-xs text-zinc-500 mt-0.5">
              Added on {new Date(document.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <span
          className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider ${statusClass[document.processing_status]}`}
        >
          {document.processing_status}
        </span>
      </div>

      {/* Progress Indicator */}
      {isWorking && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-zinc-400 mb-1">
            <span>
              {document.processing_status === "queued"
                ? "Waiting in processing queue..."
                : "Parsing, segmenting & embedding..."}
            </span>
            <span className="animate-pulse">Processing...</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-900">
            <div className="h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 animate-[loading_1.5s_infinite] w-2/3"></div>
          </div>
          {/* Custom style mapping for standard tailwind animation fallback */}
          <style jsx>{`
            @keyframes loading {
              0% { transform: translateX(-100%); }
              100% { transform: translateX(200%); }
            }
          `}</style>
        </div>
      )}

      {/* Preview text */}
      {document.raw_text_preview && !isWorking && (
        <p className="mt-4 line-clamp-3 text-xs leading-relaxed text-zinc-400 group-hover:text-zinc-300 transition-colors duration-300">
          {document.raw_text_preview}
        </p>
      )}

      {/* Error message */}
      {document.processing_error && (
        <div className="mt-4 flex items-start gap-2 rounded-lg border border-red-900/50 bg-red-950/20 p-3 text-xs text-red-300">
          <ShieldAlert size={16} className="mt-0.5 shrink-0 text-red-400" />
          <p className="leading-relaxed">{document.processing_error}</p>
        </div>
      )}

      {/* Metadata Grid */}
      <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-zinc-900 pt-4 text-xs text-zinc-400">
        <div className="flex items-center gap-1.5">
          <HardDrive size={13} className="text-zinc-600" />
          <span>Size: <strong className="text-zinc-300">{formatBytes(document.file_size)}</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <FileText size={13} className="text-zinc-600" />
          <span>Pages: <strong className="text-zinc-300">{document.page_count ?? 1}</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <Layers size={13} className="text-zinc-600" />
          <span>Chunks: <strong className="text-zinc-300">{document.chunk_count}</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock size={13} className="text-zinc-600" />
          <span>
            Time:{" "}
            <strong className="text-zinc-300">
              {document.processing_duration !== null && document.processing_duration !== undefined
                ? `${document.processing_duration.toFixed(2)}s`
                : document.processing_status === "completed"
                ? "N/A"
                : "—"}
            </strong>
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-5 flex gap-3">
        <button
          onClick={handleReprocess}
          disabled={isWorking}
          className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/50 px-3 py-1.5 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <RefreshCw size={12} className={isReprocessing ? "animate-spin" : ""} />
          Reprocess
        </button>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="ml-auto flex items-center gap-1.5 rounded-lg bg-red-950/60 border border-red-900/40 px-3 py-1.5 text-xs font-medium text-red-300 hover:bg-red-900/60 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <Trash2 size={12} />
          {isDeleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </article>
  );
}
