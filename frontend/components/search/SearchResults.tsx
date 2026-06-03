import SearchResultCard from "@/components/search/SearchResultCard";
import type { SearchResult } from "@/types/search";

type SearchResultsProps = {
  results: SearchResult[];
};

export default function SearchResults({ results }: SearchResultsProps) {
  return (
    <div className="space-y-4">
      {results.map((result) => (
        <SearchResultCard key={result.chunk_id} result={result} />
      ))}
    </div>
  );
}
