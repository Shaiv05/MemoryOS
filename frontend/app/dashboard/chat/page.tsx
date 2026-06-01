"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { sendChatMessage } from "@/services/chat";
import type { ChatResponse } from "@/types/chat";

export default function ChatPage() {
  const { token } = useAuth({ required: true });
  const [message, setMessage] = useState("");
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError("");

    try {
      const data = await sendChatMessage(message.trim(), conversationId);
      setResponse(data);
      setConversationId(data.conversation_id);
      setMessage("");
    } catch {
      setError("Chat request failed. Verify embeddings and vector search first.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) return null;

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-4xl">
          <h1 className="text-4xl font-bold">Chat</h1>
          <p className="mt-3 text-zinc-400">
            Retrieval-first scaffold. LLM answer generation stays disabled until
            ingestion and search are verified.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 flex gap-3">
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              className="flex-1 rounded bg-zinc-900 p-3 outline-none focus:ring-2 focus:ring-zinc-700"
              placeholder="Ask about your documents"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded bg-white px-4 py-2 font-medium text-black disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Searching..." : "Send"}
            </button>
          </form>

          {error && (
            <p className="mt-6 rounded border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">
              {error}
            </p>
          )}

          {response && (
            <section className="mt-8 rounded-lg border border-zinc-800 bg-zinc-950 p-6">
              <h2 className="text-xl font-semibold">Answer</h2>
              <p className="mt-3 text-zinc-300">{response.answer}</p>

              <h3 className="mt-6 text-sm font-semibold uppercase text-zinc-500">
                Sources
              </h3>
              <div className="mt-3 space-y-3">
                {response.sources.map((source) => (
                  <div
                    key={source.chunk_id}
                    className="rounded border border-zinc-800 p-3 text-sm text-zinc-300"
                  >
                    <p className="font-medium text-white">
                      {source.document_title} · chunk {source.chunk_index}
                    </p>
                    <p className="mt-2 text-zinc-400">{source.content}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
