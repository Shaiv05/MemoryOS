"use client";

import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import type { ChatMessage } from "@/types/chat";

type MessageBubbleProps = {
  message: ChatMessage;
};

const formatScore = (score: number) => `${Math.round(score * 100)}%`;

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <motion.article
        layout
        className={`max-w-[85%] rounded-2xl p-5 ${
          isUser
            ? "bg-white text-black rounded-tr-none"
            : "bg-zinc-900 border border-zinc-800 text-zinc-100 rounded-tl-none"
        }`}
      >
        <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
          {message.content}
        </div>

        {!isUser && message.sources.length > 0 && (
          <div className="mt-6 border-t border-zinc-800/60 pt-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-px flex-1 bg-zinc-800/60" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">
                Sources & Context
              </span>
              <div className="h-px flex-1 bg-zinc-800/60" />
            </div>
            
            <div className="grid gap-3 sm:grid-cols-2">
              {message.sources.map((source, index) => (
                <div
                  key={`${message.id}-${source.chunk_id}`}
                  className="group relative flex flex-col rounded-xl border border-zinc-800 bg-black/30 p-4 transition hover:border-zinc-600 hover:bg-black/50"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-zinc-800 text-[10px] font-bold text-zinc-400">
                        S{index + 1}
                      </span>
                      <p className="truncate text-xs font-semibold text-zinc-200">
                        {source.document_title}
                      </p>
                    </div>
                    <span className="shrink-0 text-[10px] font-medium text-emerald-400/80">
                      {formatScore(source.similarity_score)}
                    </span>
                  </div>
                  
                  <p className="line-clamp-3 text-[11px] leading-relaxed text-zinc-400 group-hover:text-zinc-300">
                    {source.content}
                  </p>
                  
                  <div className="mt-3 flex items-center gap-1 text-[10px] font-medium text-zinc-500 group-hover:text-zinc-300 transition-colors">
                    <ExternalLink className="h-2.5 w-2.5" />
                    View Source
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.article>
    </motion.div>
  );
}
