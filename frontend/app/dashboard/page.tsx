"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { getDashboardSummary } from "@/services/dashboard";
import type { DashboardSummary } from "@/types/dashboard";

const emptySummary: DashboardSummary = {
  documents: 0,
  completed_documents: 0,
  failed_documents: 0,
  chunks: 0,
};

export default function DashboardPage() {
  const { token } = useAuth({ required: true });
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    let ignore = false;
    getDashboardSummary()
      .then((data) => {
        if (!ignore) {
          setSummary(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [token]);

  if (!token) return null;

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-8 md:p-10">
        <div className="max-w-5xl">
          <h1 className="text-4xl font-semibold tracking-tight">
            Welcome to AI Second Brain
          </h1>

          <p className="mt-3 max-w-2xl text-zinc-400">
            Your private AI knowledge operating system for document ingestion,
            semantic search, and grounded RAG.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
              <p className="text-sm text-zinc-400">Documents</p>
              <p className="mt-2 text-3xl font-semibold">
                {loading ? "..." : summary.documents}
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
              <p className="text-sm text-zinc-400">Completed</p>
              <p className="mt-2 text-3xl font-semibold">
                {loading ? "..." : summary.completed_documents}
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
              <p className="text-sm text-zinc-400">Chunks</p>
              <p className="mt-2 text-3xl font-semibold">
                {loading ? "..." : summary.chunks}
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
              <p className="text-sm text-zinc-400">Failed</p>
              <p className="mt-2 text-3xl font-semibold">
                {loading ? "..." : summary.failed_documents}
              </p>
            </div>
          </div>

          <div className="mt-8 rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-8">
            <h2 className="text-xl font-medium">Current phase</h2>

            <p className="mt-2 text-zinc-400">
              Stabilize document extraction, chunking, embeddings, and vector
              search before expanding chat behavior.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
