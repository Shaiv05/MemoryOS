"use client";

import { AnimatePresence, motion } from "framer-motion";
import MessageBubble from "@/components/chat/MessageBubble";
import type { ChatMessage } from "@/types/chat";

type MessageListProps = {
  messages: ChatMessage[];
  loading: boolean;
};

export default function MessageList({ messages, loading }: MessageListProps) {
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
          <MessageBubble key={message.id} message={message} />
        ))}
      </AnimatePresence>

      {loading && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-start"
        >
          <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-400">
            Retrieving context and drafting an answer...
          </div>
        </motion.div>
      )}
    </div>
  );
}
