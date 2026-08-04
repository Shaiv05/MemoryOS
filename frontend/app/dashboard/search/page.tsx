"use client";

import { FormEvent, useState } from "react";
import { Search, Filter, SlidersHorizontal } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import SearchResults from "@/components/search/SearchResults";
import { useAuth } from "@/hooks/useAuth";
import { getApiErrorMessage, searchDocuments } from "@/services/search";
import type { SearchResult } from "@/types/search";

const fileTypeOptions = [
  { id: "", label: "All Types" },
  { id: "pdf", label: "PDF" },
  { id: "docx", label: "DOCX" },
  { id: "txt", label: "TXT & MD" },
  { id: "note", label: "Notes" },
  { id: "link", label: "Links" },
];

export default function SearchPage() {
  const { token } = useAuth({ required: true });
  const [query, setQuery] = useState("");
  const [searchedQuery, setSearchedQuery] = useState("");
  const [selectedFileType, setSelectedFileType] = useState("");
  const [minScore, setMinScore] = useState(0.20);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (overrideQuery?: string, overrideType?: string) => {
    const q = (overrideQuery !== undefined ? overrideQuery : query).trim();
    if (!q) return;

    const fType = overrideType !== undefined ? overrideType : selectedFileType;

    setLoading(true);
    setError("");
    setHasSearched(true);
    setSearchedQuery(q);

    try {
      const data = await searchDocuments({
        query: q,
        limit: 12,
        min_score: minScore,
        file_type: fType || undefined,
      });
      setResults(data);
    } catch (err: unknown) {
      setResults([]);
      setError(getApiErrorMessage(err, "Search failed. Try again."));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    handleSearch();
  };

  const handleFileTypeChange = (typeId: string) => {
    setSelectedFileType(typeId);
    if (hasSearched && query.trim()) {
      handleSearch(query, typeId);
    }
  };

  if (!token) return null;

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-6 md:p-10">
        <div className="max-w-5xl">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Semantic & Hybrid Search</h1>
              <p className="mt-2 max-w-2xl text-sm text-zinc-400">
                Precision hybrid vector + keyword search with automatic relevance thresholding.
              </p>
            </div>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSubmit} className="mt-8">
            <div className="flex flex-col gap-3 rounded-xl border border-zinc-800/80 bg-zinc-950/80 p-3 backdrop-blur-md md:flex-row">
              <div className="flex min-w-0 flex-1 items-center gap-3 rounded-lg bg-black px-4 py-1 border border-zinc-800/50 focus-within:border-zinc-600 transition-colors">
                <Search className="h-5 w-5 shrink-0 text-zinc-500" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="min-h-12 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
                  placeholder="Search your knowledge base (e.g., 'sales report 2025' or 'database architecture')..."
                />
              </div>

              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Filter controls */}
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2 overflow-x-auto py-1">
                <Filter size={14} className="text-zinc-500 shrink-0" />
                <span className="text-xs text-zinc-500 font-medium mr-1">Filter:</span>
                {fileTypeOptions.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => handleFileTypeChange(opt.id)}
                    className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
                      selectedFileType === opt.id
                        ? "border-white bg-white text-black font-semibold"
                        : "border-zinc-800 bg-zinc-950 text-zinc-400 hover:border-zinc-700 hover:text-white"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2 text-xs text-zinc-400">
                <SlidersHorizontal size={14} className="text-zinc-500" />
                <span>Min Match Cutoff:</span>
                <input
                  type="range"
                  min="0.10"
                  max="0.50"
                  step="0.05"
                  value={minScore}
                  onChange={(e) => setMinScore(parseFloat(e.target.value))}
                  className="w-20 accent-white cursor-pointer"
                />
                <span className="font-mono text-zinc-300">{Math.round(minScore * 100)}%</span>
              </div>
            </div>
          </form>

          {error && (
            <p className="mt-6 rounded-lg border border-red-900/60 bg-red-950/60 p-4 text-sm text-red-300">
              {error}
            </p>
          )}

          {/* Results section */}
          <section className="mt-8">
            {loading && (
              <div className="space-y-4">
                {[0, 1, 2].map((item) => (
                  <div
                    key={item}
                    className="h-36 animate-pulse rounded-xl border border-zinc-800/80 bg-zinc-950/40"
                  />
                ))}
              </div>
            )}

            {!loading && !hasSearched && (
              <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-950/40 p-10 text-center text-zinc-500">
                Enter a query above to retrieve highly matching semantic chunks. Irrelevant documents are automatically filtered out.
              </div>
            )}

            {!loading && hasSearched && !error && results.length === 0 && (
              <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-950/60 p-10 text-center">
                <h2 className="text-lg font-semibold text-white">No relevant matches found</h2>
                <p className="mt-2 text-sm text-zinc-400">
                  No processed document chunks matched &quot;{searchedQuery}&quot; above the threshold. Try adjusting terms or lowering the match cutoff.
                </p>
              </div>
            )}

            {!loading && results.length > 0 && (
              <>
                <div className="mb-4 flex items-center justify-between text-xs text-zinc-400">
                  <p>
                    Showing <strong className="text-white">{results.length}</strong> highly relevant result{results.length === 1 ? "" : "s"} for &quot;<span className="text-zinc-200">{searchedQuery}</span>&quot;
                  </p>
                </div>
                <SearchResults results={results} />
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
