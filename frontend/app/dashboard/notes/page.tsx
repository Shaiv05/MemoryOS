"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2, Edit3, BookOpen } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { getNotes, createNote, updateNote, deleteNote } from "@/services/productivity";
import type { Note } from "@/types/productivity";

export default function NotesPage() {
  const { token } = useAuth({ required: true });
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingNote, setEditingNote] = useState<Partial<Note> | null>(null);

  useEffect(() => {
    if (token) {
      getNotes().then(setNotes).finally(() => setLoading(false));
    }
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingNote?.title || !editingNote?.content) return;

    if (editingNote.id) {
      const updated = await updateNote(editingNote.id, editingNote);
      setNotes(notes.map((n) => (n.id === updated.id ? updated : n)));
    } else {
      const created = await createNote(editingNote);
      setNotes([created, ...notes]);
    }
    setEditingNote(null);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    await deleteNote(id);
    setNotes(notes.filter((n) => n.id !== id));
  };

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />
      <main className="flex-1 p-10 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Notes</h1>
              <p className="text-zinc-400 mt-2">Capture your thoughts and link them to knowledge.</p>
            </div>
            <button
              onClick={() => setEditingNote({ title: "", content: "" })}
              className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition"
            >
              <Plus className="h-4 w-4" />
              New Note
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AnimatePresence>
              {notes.map((note) => (
                <motion.div
                  key={note.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition group"
                >
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-semibold">{note.title}</h3>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                      <button onClick={() => setEditingNote(note)} className="p-1 hover:text-blue-400">
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDelete(note.id)} className="p-1 hover:text-red-400">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <p className="text-zinc-400 line-clamp-4 text-sm leading-relaxed">
                    {note.content}
                  </p>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {editingNote && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 z-50">
              <motion.form
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                onSubmit={handleSave}
                className="bg-zinc-950 border border-zinc-800 w-full max-w-2xl p-8 rounded-3xl shadow-2xl"
              >
                <h2 className="text-2xl font-bold mb-6">
                  {editingNote.id ? "Edit Note" : "New Note"}
                </h2>
                <input
                  autoFocus
                  value={editingNote.title}
                  onChange={(e) => setEditingNote({ ...editingNote, title: e.target.value })}
                  placeholder="Title"
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 focus:outline-none focus:border-zinc-500 transition"
                />
                <textarea
                  value={editingNote.content}
                  onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                  placeholder="Content..."
                  rows={10}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-6 focus:outline-none focus:border-zinc-500 transition resize-none"
                />
                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setEditingNote(null)}
                    className="px-6 py-2 text-zinc-400 hover:text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-white text-black px-6 py-2 rounded-xl font-bold hover:bg-zinc-200 transition"
                  >
                    Save Note
                  </button>
                </div>
              </motion.form>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
