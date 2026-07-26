"use client";

import { AnimatePresence, motion } from "framer-motion";
import MessageBubble from "@/components/chat/MessageBubble";
import type { ChatMessage } from "@/types/chat";

type MessageListProps = {
  messages: ChatMessage[];
  loading: boolean;
  onRetry: () => void;
  onRegenerate: () => void;
};

export default function MessageList({
  messages,
  loading,
  onRetry,
  onRegenerate,
}: MessageListProps) {
  const lastAssistantId = [...messages].reverse().find((item) => item.role === "assistant")?.id;
  if (messages.length === 0 && !loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-8 text-zinc-400"
      >
        Ask a question to start a document-grounded conversation.
      </motion.div>
    );
  }

  return (
    <div className="space-y-5">
      <AnimatePresence initial={false}>
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isLastAssistant={message.role === "assistant" && lastAssistantId === message.id}
            onRetry={onRetry}
            onRegenerate={onRegenerate}
          />
        ))}
      </AnimatePresence>

      {loading && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-start"
        >
          <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-400">
            <span className="inline-flex items-center gap-1">
              Drafting
              <span className="animate-pulse">.</span>
              <span className="animate-pulse delay-150">.</span>
              <span className="animate-pulse delay-300">.</span>
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
