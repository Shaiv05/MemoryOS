"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Brain, FileText, CheckSquare, Layers } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { getDashboardSummary, getAiSummary } from "@/services/dashboard";
import type { DashboardSummary } from "@/types/dashboard";

const emptySummary: DashboardSummary = {
  documents: 0,
  completed_documents: 0,
  memories: 0,
  pending_tasks: 0,
  chunks: 0,
};

export default function DashboardPage() {
  const { token } = useAuth({ required: true });
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [aiSummary, setAiSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingAi, setLoadingAi] = useState(true);

  useEffect(() => {
    if (!token) return;

    getDashboardSummary()
      .then(setSummary)
      .finally(() => setLoading(false));

    getAiSummary()
      .then((data) => setAiSummary(data.summary))
      .finally(() => setLoadingAi(false));
  }, [token]);

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <Sidebar />

      <main className="flex-1 p-10 overflow-y-auto custom-scrollbar">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-6xl mx-auto"
        >
          <header className="mb-12">
            <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">
              MemoryOS
            </h1>
            <p className="mt-4 text-xl text-zinc-400 max-w-2xl leading-relaxed">
              Your private knowledge operating system is active. Everything is connected.
            </p>
          </header>

          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Sparkles className="h-5 w-5 text-emerald-400" />
              <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500">Daily Intelligence</h2>
            </div>
            <div className="p-8 rounded-3xl bg-zinc-900 border border-zinc-800 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition">
                <Brain className="h-32 w-32" />
              </div>
              <div className="relative z-10">
                {loadingAi ? (
                  <div className="space-y-3">
                    <div className="h-4 bg-zinc-800 rounded-full w-3/4 animate-pulse" />
                    <div className="h-4 bg-zinc-800 rounded-full w-1/2 animate-pulse" />
                    <div className="h-4 bg-zinc-800 rounded-full w-2/3 animate-pulse" />
                  </div>
                ) : (
                  <p className="text-xl text-zinc-200 leading-relaxed font-medium">
                    {aiSummary || "Ingest more documents to generate your daily intelligence summary."}
                  </p>
                )}
              </div>
            </div>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-12">
            <StatCard label="Documents" value={summary.documents} icon={<FileText className="h-4 w-4" />} />
            <StatCard label="Processed" value={summary.completed_documents} icon={<Layers className="h-4 w-4" />} />
            <StatCard label="Memories" value={summary.memories} icon={<Brain className="h-4 w-4" />} />
            <StatCard label="Tasks" value={summary.pending_tasks} icon={<CheckSquare className="h-4 w-4" />} />
            <StatCard label="Chunks" value={summary.chunks} icon={<Layers className="h-4 w-4" />} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 p-8 rounded-3xl bg-zinc-950 border border-zinc-800 border-dashed flex flex-col items-center justify-center text-center">
              <h3 className="text-xl font-bold mb-2">Project Evolution</h3>
              <p className="text-zinc-500 text-sm max-w-sm">
                MemoryOS has reached Phase 10. Advanced reasoning and cross-document intelligence are now operational.
              </p>
            </div>
            <div className="p-8 rounded-3xl bg-emerald-500/5 border border-emerald-500/20">
              <h3 className="text-lg font-bold text-emerald-400 mb-4">System Health</h3>
              <div className="space-y-4">
                <HealthItem label="Graph Extraction" status="online" />
                <HealthItem label="Vector Database" status="online" />
                <HealthItem label="LLM Reasoning" status="online" />
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <div className="p-6 rounded-2xl bg-zinc-900 border border-zinc-800">
      <div className="flex items-center gap-2 text-zinc-500 mb-3">
        {icon}
        <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>
      </div>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

function HealthItem({ label, status }: { label: string; status: string }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-zinc-400">{label}</span>
      <span className="flex items-center gap-2 text-emerald-400 font-bold uppercase text-[10px] tracking-widest">
        <div className="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse" />
        {status}
      </span>
    </div>
  );
}
