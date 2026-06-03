"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Plus, Trash2 } from "lucide-react";
import MessageInput from "@/components/chat/MessageInput";
import MessageList from "@/components/chat/MessageList";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import {
  deleteChatConversation,
  getChatConversation,
  getChatConversations,
  sendChatMessage,
} from "@/services/chat";
import { getApiErrorMessage } from "@/services/search";
import type { ChatConversation, ChatMessage } from "@/types/chat";

const createLocalMessage = (
  role: ChatMessage["role"],
  content: string,
  sources: ChatMessage["sources"] = []
): ChatMessage => ({
  id: -Date.now(),
  role,
  content,
  sources,
  created_at: new Date().toISOString(),
});

export default function ChatPage() {
  const { token } = useAuth({ required: true });
  const [message, setMessage] = useState("");
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState("");

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token) return;

    let ignore = false;
    getChatConversations()
      .then((data) => {
        if (!ignore) setConversations(data);
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(getApiErrorMessage(err, "Could not load conversations."));
        }
      })
      .finally(() => {
        if (!ignore) setLoadingHistory(false);
      });

    return () => {
      ignore = true;
    };
  }, [token]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const refreshConversations = async () => {
    const data = await getChatConversations();
    setConversations(data);
  };

  const selectConversation = async (id: number) => {
    if (loadingMessages) return;
    setError("");
    setConversationId(id);
    setLoadingMessages(true);

    try {
      const data = await getChatConversation(id);
      setMessages(data.messages);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Could not load this conversation."));
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleDeleteConversation = async (event: React.MouseEvent, id: number) => {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;

    try {
      await deleteChatConversation(id);
      setConversations((current) => current.filter((c) => c.id !== id));
      if (conversationId === id) {
        startNewConversation();
      }
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Could not delete conversation."));
    }
  };

  const startNewConversation = () => {
    setConversationId(undefined);
    setMessages([]);
    setMessage("");
    setError("");
  };

  const handleSend = async () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || loading) return;

    setLoading(true);
    setError("");
    setMessage("");
    setMessages((current) => [
      ...current,
      createLocalMessage("user", trimmedMessage),
    ]);

    try {
      const data = await sendChatMessage(trimmedMessage, conversationId);
      setConversationId(data.conversation_id);
      setMessages((current) => [
        ...current,
        {
          id: data.message_id,
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          created_at: new Date().toISOString(),
        },
      ]);
      await refreshConversations();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Chat request failed."));
    } finally {
      setLoading(false);
    }
  };

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />

      <main className="flex min-w-0 flex-1 overflow-hidden">
        <motion.aside
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          className="hidden w-80 shrink-0 border-r border-zinc-800 bg-zinc-950 p-5 lg:flex lg:flex-col"
        >
          <button
            onClick={startNewConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-3 text-sm font-medium text-black transition hover:bg-zinc-200"
          >
            <Plus className="h-4 w-4" />
            New chat
          </button>

          <div className="mt-6 flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            {loadingHistory && conversations.length === 0 ? (
              <div className="space-y-2">
                {[0, 1, 2, 3].map((i) => (
                  <div key={i} className="h-12 animate-pulse rounded-lg bg-zinc-900" />
                ))}
              </div>
            ) : conversations.length === 0 ? (
              <p className="text-sm text-zinc-500">No conversations yet.</p>
            ) : (
              conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => selectConversation(conversation.id)}
                  className={`group relative flex w-full cursor-pointer items-center rounded-lg px-3 py-3 text-left text-sm transition ${
                    conversationId === conversation.id
                      ? "bg-zinc-800 text-white"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                  }`}
                >
                  <span className="line-clamp-1 flex-1 pr-6">
                    {conversation.title || "Untitled chat"}
                  </span>
                  <button
                    onClick={(e) => handleDeleteConversation(e, conversation.id)}
                    className="absolute right-2 opacity-0 group-hover:opacity-100 transition p-1 hover:text-red-400"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </motion.aside>

        <motion.section
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex min-w-0 flex-1 flex-col overflow-hidden"
        >
          <div className="border-b border-zinc-800 bg-black p-6 md:px-10">
            <div className="max-w-4xl">
              <h1 className="text-2xl font-semibold tracking-tight">
                Chat With Documents
              </h1>
              <p className="mt-1 text-sm text-zinc-400">
                Grounded search & retrieval over your processed data.
              </p>
            </div>
          </div>

          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 md:p-10 custom-scrollbar"
          >
            <div className="mx-auto max-w-4xl">
              {error && (
                <p className="mb-6 rounded border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">
                  {error}
                </p>
              )}

              {loadingMessages ? (
                <div className="space-y-6">
                  {[0, 1].map((i) => (
                    <div key={i} className="flex gap-4">
                      <div className="h-10 w-10 shrink-0 animate-pulse rounded bg-zinc-900" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 w-1/4 animate-pulse rounded bg-zinc-900" />
                        <div className="h-20 animate-pulse rounded bg-zinc-900" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <MessageList messages={messages} loading={loading} />
              )}
            </div>
          </div>

          <div className="border-t border-zinc-800 bg-black p-6 md:px-10">
            <div className="mx-auto max-w-4xl">
              <MessageInput
                value={message}
                loading={loading}
                onChange={setMessage}
                onSubmit={handleSend}
              />
            </div>
          </div>
        </motion.section>
      </main>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #27272a;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #3f3f46;
        }
      `}</style>
    </div>
  );
}
