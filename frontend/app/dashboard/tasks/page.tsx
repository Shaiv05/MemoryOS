"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2, CheckCircle, Circle, AlertCircle } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { getTasks, createTask, updateTask, deleteTask } from "@/services/productivity";
import type { Task } from "@/types/productivity";

export default function TasksPage() {
  const { token } = useAuth({ required: true });
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingTask, setEditingTask] = useState<Partial<Task> | null>(null);

  useEffect(() => {
    if (token) {
      getTasks().then(setTasks).finally(() => setLoading(false));
    }
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask?.title) return;

    if (editingTask.id) {
      const updated = await updateTask(editingTask.id, editingTask);
      setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)));
    } else {
      const created = await createTask({ ...editingTask, status: "pending" });
      setTasks([created, ...tasks]);
    }
    setEditingTask(null);
  };

  const toggleStatus = async (task: Task) => {
    const newStatus = task.status === "completed" ? "pending" : "completed";
    const updated = await updateTask(task.id, { status: newStatus });
    setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)));
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    await deleteTask(id);
    setTasks(tasks.filter((t) => t.id !== id));
  };

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />
      <main className="flex-1 p-10 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Tasks</h1>
              <p className="text-zinc-400 mt-2">Manage your execution pipeline.</p>
            </div>
            <button
              onClick={() => setEditingTask({ title: "", description: "", priority: "medium" })}
              className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition"
            >
              <Plus className="h-4 w-4" />
              Add Task
            </button>
          </div>

          <div className="space-y-3">
            <AnimatePresence>
              {tasks.map((task) => (
                <motion.div
                  key={task.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition ${
                    task.status === "completed"
                      ? "bg-zinc-900/50 border-zinc-800 opacity-60"
                      : "bg-zinc-900 border-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  <button
                    onClick={() => toggleStatus(task)}
                    className="text-zinc-500 hover:text-white transition"
                  >
                    {task.status === "completed" ? (
                      <CheckCircle className="h-6 w-6 text-emerald-500" />
                    ) : (
                      <Circle className="h-6 w-6" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0" onClick={() => setEditingTask(task)}>
                    <h3 className={`font-semibold truncate ${task.status === "completed" ? "line-through" : ""}`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-xs text-zinc-500 truncate mt-0.5">{task.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${
                      task.priority === "high" ? "border-red-900 text-red-400 bg-red-950/20" :
                      task.priority === "medium" ? "border-amber-900 text-amber-400 bg-amber-950/20" :
                      "border-zinc-700 text-zinc-400 bg-zinc-800/20"
                    }`}>
                      {task.priority}
                    </span>
                    <button onClick={() => handleDelete(task.id)} className="p-1 hover:text-red-400 transition">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {editingTask && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 z-50">
              <motion.form
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                onSubmit={handleSave}
                className="bg-zinc-950 border border-zinc-800 w-full max-w-lg p-8 rounded-3xl shadow-2xl"
              >
                <h2 className="text-2xl font-bold mb-6">
                  {editingTask.id ? "Edit Task" : "Add Task"}
                </h2>
                <div className="space-y-4">
                  <input
                    autoFocus
                    value={editingTask.title}
                    onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                    placeholder="What needs to be done?"
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 focus:outline-none focus:border-zinc-500 transition"
                  />
                  <textarea
                    value={editingTask.description}
                    onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                    placeholder="Description (optional)"
                    rows={3}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 focus:outline-none focus:border-zinc-500 transition resize-none"
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1 block">Priority</label>
                      <select
                        value={editingTask.priority}
                        onChange={(e) => setEditingTask({ ...editingTask, priority: e.target.value as any })}
                        className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-3 focus:outline-none focus:border-zinc-500 transition"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1 block">Due Date</label>
                      <input
                        type="date"
                        value={editingTask.due_date?.split("T")[0] || ""}
                        onChange={(e) => setEditingTask({ ...editingTask, due_date: e.target.value })}
                        className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-3 focus:outline-none focus:border-zinc-500 transition"
                      />
                    </div>
                  </div>
                </div>
                <div className="flex justify-end gap-3 mt-8">
                  <button
                    type="button"
                    onClick={() => setEditingTask(null)}
                    className="px-6 py-2 text-zinc-400 hover:text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-white text-black px-6 py-2 rounded-xl font-bold hover:bg-zinc-200 transition"
                  >
                    Save Task
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
