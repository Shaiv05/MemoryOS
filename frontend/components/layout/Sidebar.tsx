"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Brain,
  FileText,
  MessageSquare,
  Search,
  Share2,
  BookOpen,
  CheckSquare,
  Target,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  const linkClass = (href: string) => {
    const active = pathname === href;
    return `flex items-center gap-3 rounded-xl px-4 py-3 transition ${
      active
        ? "bg-zinc-900 text-zinc-100"
        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
    }`;
  };

  return (
    <aside className="flex h-screen w-72 flex-col border-r border-zinc-800 bg-zinc-950 px-5 py-6 text-white overflow-hidden">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">AI Second Brain</h1>
        <p className="mt-1 text-sm text-zinc-400">Your private knowledge OS</p>
      </div>

      <nav className="mt-10 flex-1 space-y-2 text-sm overflow-y-auto pr-2 custom-scrollbar">
        <Link href="/dashboard" className={linkClass("/dashboard")}>
          <LayoutDashboard className="h-4 w-4" />
          Dashboard
        </Link>

        <Link href="/dashboard/documents" className={linkClass("/dashboard/documents")}>
          <FileText className="h-4 w-4" />
          Documents
        </Link>

        <Link href="/dashboard/search" className={linkClass("/dashboard/search")}>
          <Search className="h-4 w-4" />
          Search
        </Link>

        <Link href="/dashboard/chat" className={linkClass("/dashboard/chat")}>
          <MessageSquare className="h-4 w-4" />
          Chats
        </Link>

        <Link href="/dashboard/memory" className={linkClass("/dashboard/memory")}>
          <Brain className="h-4 w-4" />
          Memory
        </Link>

        <Link href="/dashboard/graph" className={linkClass("/dashboard/graph")}>
          <Share2 className="h-4 w-4" />
          Graph
        </Link>

        <div className="pt-4 pb-2 px-4">
          <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Productivity</span>
        </div>

        <Link href="/dashboard/notes" className={linkClass("/dashboard/notes")}>
          <BookOpen className="h-4 w-4" />
          Notes
        </Link>

        <Link href="/dashboard/tasks" className={linkClass("/dashboard/tasks")}>
          <CheckSquare className="h-4 w-4" />
          Tasks
        </Link>

        <Link href="/dashboard/goals" className={linkClass("/dashboard/goals")}>
          <Target className="h-4 w-4" />
          Goals
        </Link>

        <a
          href="#"
          className="flex items-center gap-3 rounded-xl px-4 py-3 text-zinc-400 transition hover:bg-zinc-900 hover:text-zinc-100"
        >
          <Settings className="h-4 w-4" />
          Settings
        </a>
      </nav>

      <button
        onClick={logout}
        className="mt-6 flex items-center gap-3 rounded-xl border border-zinc-800 px-4 py-3 text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white"
      >
        <LogOut className="h-4 w-4" />
        Logout
      </button>

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
    </aside>
  );
}
