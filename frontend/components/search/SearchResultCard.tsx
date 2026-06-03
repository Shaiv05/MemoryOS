import type { SearchResult } from "@/types/search";

type SearchResultCardProps = {
  result: SearchResult;
};

const formatScore = (score: number) => `${Math.round(score * 100)}%`;

export default function SearchResultCard({ result }: SearchResultCardProps) {
  return (
    <article className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">
            {result.document_title}
          </h2>
          <p className="mt-1 text-xs uppercase tracking-wide text-zinc-500">
            Chunk {result.chunk_index}
          </p>
        </div>

        <span className="rounded-full border border-emerald-900/70 bg-emerald-950/50 px-3 py-1 text-xs font-medium text-emerald-300">
          {formatScore(result.similarity_score)}
        </span>
      </div>

      <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-zinc-300">
        {result.content}
      </p>
    </article>
  );
}
