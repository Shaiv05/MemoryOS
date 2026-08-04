"use client";

import type { SearchResult } from "@/types/search";
import { FileText, Layers, Bookmark } from "lucide-react";

type SearchResultCardProps = {
  result: SearchResult;
};

const formatScore = (score: number) => `${Math.round(score * 100)}% Match`;

export default function SearchResultCard({ result }: SearchResultCardProps) {
  const score = result.relevance_score ?? result.similarity_score;
  const pageNum = result.metadata?.page_number;

  const scoreBadgeColor =
    score >= 0.7
      ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
      : score >= 0.45
      ? "border-amber-500/40 bg-amber-500/10 text-amber-400"
      : "border-blue-500/40 bg-blue-500/10 text-blue-400";

  return (
    <article className="group rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-5 backdrop-blur-sm transition-all duration-300 hover:border-zinc-700 hover:bg-zinc-900/30">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-lg bg-zinc-900 p-2 text-zinc-400 group-hover:text-white transition-colors">
            <FileText size={18} />
          </div>
          <div>
            <h2 className="text-base font-semibold text-zinc-100 group-hover:text-white transition-colors">
              {result.document_title}
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-zinc-400">
              <span className="flex items-center gap-1">
                <Layers size={12} className="text-zinc-400" />
                Chunk {result.chunk_index + 1}
              </span>
              {pageNum && (
                <span className="flex items-center gap-1">
                  <Bookmark size={12} className="text-zinc-400" />
                  Page {pageNum}
                </span>
              )}
              {result.file_type && (
                <span className="rounded bg-zinc-900 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-zinc-300 border border-zinc-800">
                  {result.file_type}
                </span>
              )}
            </div>
          </div>
        </div>

        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${scoreBadgeColor}`}>
          {formatScore(score)}
        </span>
      </div>

      <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed text-zinc-300 border-t border-zinc-900 pt-3">
        {result.content}
      </p>
    </article>
  );
}
