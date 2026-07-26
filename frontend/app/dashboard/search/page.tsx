"use client";

import { FormEvent, useState } from "react";
import { Search } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import SearchResults from "@/components/search/SearchResults";
import { useAuth } from "@/hooks/useAuth";
import { getApiErrorMessage, searchDocuments } from "@/services/search";
import type { SearchResult } from "@/types/search";

export default function SearchPage() {
  const { token } = useAuth({ required: true });
  const [query, setQuery] = useState("");
  const [searchedQuery, setSearchedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    setLoading(true);
    setError("");
    setHasSearched(true);
    setSearchedQuery(trimmedQuery);

    try {
      const data = await searchDocuments({ query: trimmedQuery, limit: 10 });
      setResults(data);
    } catch (err: unknown) {
      setResults([]);
      setError(getApiErrorMessage(err, "Search failed. Try again."));
    } finally {
      setLoading(false);
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
              <h1 className="text-4xl font-semibold tracking-tight">
                Semantic Search
              </h1>
              <p className="mt-3 max-w-2xl text-zinc-400">
                Search across processed document chunks with vector retrieval.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-8">
            <div className="flex flex-col gap-3 rounded-lg border border-zinc-800 bg-zinc-950 p-3 md:flex-row">
              <div className="flex min-w-0 flex-1 items-center gap-3 rounded bg-black px-4">
                <Search className="h-5 w-5 shrink-0 text-zinc-500" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="min-h-12 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
                  placeholder="Search your documents"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="rounded bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>
          </form>

          {error && (
            <p className="mt-6 rounded border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">
              {error}
            </p>
          )}

          <section className="mt-8">
            {loading && (
              <div className="space-y-4">
                {[0, 1, 2].map((item) => (
                  <div
                    key={item}
                    className="h-36 animate-pulse rounded-lg border border-zinc-800 bg-zinc-950"
                  />
                ))}
              </div>
            )}

            {!loading && !hasSearched && (
              <div className="rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-8 text-zinc-400">
                Enter a query to retrieve matching chunks from your documents.
              </div>
            )}

            {!loading && hasSearched && !error && results.length === 0 && (
              <div className="rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-8">
                <h2 className="text-lg font-medium text-white">
                  No matches found
                </h2>
                <p className="mt-2 text-sm text-zinc-400">
                  No processed document chunks matched &quot;{searchedQuery}&quot;.
                </p>
              </div>
            )}

            {!loading && results.length > 0 && (
              <>
                <p className="mb-4 text-sm text-zinc-500">
                  {results.length} result{results.length === 1 ? "" : "s"} for
                  &quot;{searchedQuery}&quot;
                </p>
                <SearchResults results={results} />
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
