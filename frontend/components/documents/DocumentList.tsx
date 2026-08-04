"use client";

import { useState } from "react";
import DocumentCard from "@/components/documents/DocumentCard";
import type { Document } from "@/types/document";
import { CheckSquare, Square, Trash2, RefreshCw, CheckCircle2 } from "lucide-react";

type DocumentListProps = {
  documents: Document[];
  onDelete: (id: number) => Promise<void>;
  onReprocess: (id: number) => Promise<void>;
  onBatchDelete?: (ids: number[]) => Promise<void>;
  onBatchReprocess?: (ids: number[]) => Promise<void>;
};

export default function DocumentList({
  documents,
  onDelete,
  onReprocess,
  onBatchDelete,
  onBatchReprocess,
}: DocumentListProps) {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [isBatchWorking, setIsBatchWorking] = useState(false);

  if (documents.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-950/40 p-10 text-center text-zinc-500">
        No documents uploaded yet. Add a PDF, DOCX, TXT, note, or link above.
      </div>
    );
  }

  const allSelected = documents.length > 0 && selectedIds.length === documents.length;
  const someSelected = selectedIds.length > 0;

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedIds([]);
    } else {
      setSelectedIds(documents.map((d) => d.id));
    }
  };

  const toggleSelectOne = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleBatchDelete = async () => {
    if (!selectedIds.length) return;
    if (confirm(`Are you sure you want to delete ${selectedIds.length} selected document(s)?`)) {
      setIsBatchWorking(true);
      try {
        if (onBatchDelete) {
          await onBatchDelete(selectedIds);
        } else {
          for (const id of selectedIds) {
            await onDelete(id);
          }
        }
        setSelectedIds([]);
      } finally {
        setIsBatchWorking(false);
      }
    }
  };

  const handleBatchReprocess = async () => {
    if (!selectedIds.length) return;
    setIsBatchWorking(true);
    try {
      if (onBatchReprocess) {
        await onBatchReprocess(selectedIds);
      } else {
        for (const id of selectedIds) {
          await onReprocess(id);
        }
      }
    } finally {
      setIsBatchWorking(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Batch Control Toolbar */}
      <div className="sticky top-4 z-20 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-950/90 px-4 py-3 backdrop-blur-md shadow-xl transition-all">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSelectAll}
            className="flex items-center gap-2.5 text-xs font-semibold text-zinc-300 hover:text-white transition-colors"
          >
            {allSelected ? (
              <CheckSquare className="h-4.5 w-4.5 text-purple-400" />
            ) : (
              <Square className="h-4.5 w-4.5 text-zinc-500" />
            )}
            <span>{allSelected ? "Deselect All" : "Select All"}</span>
          </button>

          {someSelected && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-0.5 text-xs font-semibold text-purple-300 animate-in fade-in">
              <CheckCircle2 size={12} />
              {selectedIds.length} selected
            </span>
          )}
        </div>

        {someSelected && (
          <div className="flex items-center gap-2 animate-in fade-in">
            <button
              onClick={handleBatchReprocess}
              disabled={isBatchWorking}
              className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:bg-zinc-800 hover:text-white disabled:opacity-50 transition-all"
            >
              <RefreshCw size={13} className={isBatchWorking ? "animate-spin" : ""} />
              Reprocess ({selectedIds.length})
            </button>
            <button
              onClick={handleBatchDelete}
              disabled={isBatchWorking}
              className="flex items-center gap-1.5 rounded-lg border border-red-900/50 bg-red-950/60 px-3 py-1.5 text-xs font-medium text-red-300 hover:bg-red-900/70 hover:text-white disabled:opacity-50 transition-all"
            >
              <Trash2 size={13} />
              Delete ({selectedIds.length})
            </button>
          </div>
        )}
      </div>

      {/* Document List Cards */}
      <div className="space-y-4">
        {documents.map((document) => (
          <DocumentCard
            key={document.id}
            document={document}
            onDelete={onDelete}
            onReprocess={onReprocess}
            isSelected={selectedIds.includes(document.id)}
            onToggleSelect={() => toggleSelectOne(document.id)}
          />
        ))}
      </div>
    </div>
  );
}
