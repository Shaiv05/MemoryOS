"use client";

import DocumentCard from "@/components/documents/DocumentCard";
import type { Document } from "@/types/document";

type DocumentListProps = {
  documents: Document[];
  onDelete: (id: number) => Promise<void>;
  onReprocess: (id: number) => Promise<void>;
};

export default function DocumentList({
  documents,
  onDelete,
  onReprocess,
}: DocumentListProps) {
  if (documents.length === 0) {
    return <p className="text-zinc-400">No documents yet.</p>;
  }

  return (
    <div className="space-y-4">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          onDelete={onDelete}
          onReprocess={onReprocess}
        />
      ))}
    </div>
  );
}
