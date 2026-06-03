"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2, Target, Trophy } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { getGoals, createGoal, updateGoal, deleteGoal } from "@/services/productivity";
import type { Goal } from "@/types/productivity";

export default function GoalsPage() {
  const { token } = useAuth({ required: true });
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingGoal, setEditingGoal] = useState<Partial<Goal> | null>(null);

  useEffect(() => {
    if (token) {
      getGoals().then(setGoals).finally(() => setLoading(false));
    }
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingGoal?.title) return;

    if (editingGoal.id) {
      const updated = await updateGoal(editingGoal.id, editingGoal);
      setGoals(goals.map((g) => (g.id === updated.id ? updated : g)));
    } else {
      const created = await createGoal({ ...editingGoal, progress: 0, is_completed: false });
      setGoals([created, ...goals]);
    }
    setEditingGoal(null);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    await deleteGoal(id);
    setGoals(goals.filter((g) => g.id !== id));
  };

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />
      <main className="flex-1 p-10 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Goals</h1>
              <p className="text-zinc-400 mt-2">Define your long-term vision and track progress.</p>
            </div>
            <button
              onClick={() => setEditingGoal({ title: "", description: "", progress: 0 })}
              className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition"
            >
              <Plus className="h-4 w-4" />
              Set New Goal
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6">
            <AnimatePresence>
              {goals.map((goal) => (
                <motion.div
                  key={goal.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="p-8 rounded-3xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition relative overflow-hidden group"
                >
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-zinc-950 rounded-2xl border border-zinc-800">
                        <Target className="h-6 w-6 text-emerald-400" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold">{goal.title}</h3>
                        {goal.target_date && (
                          <p className="text-xs text-zinc-500 mt-1">Target: {new Date(goal.target_date).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                      <button onClick={() => setEditingGoal(goal)} className="p-2 bg-zinc-950 border border-zinc-800 rounded-xl hover:text-blue-400 transition">
                        <Plus className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDelete(goal.id)} className="p-2 bg-zinc-950 border border-zinc-800 rounded-xl hover:text-red-400 transition">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <p className="text-zinc-400 mb-8 max-w-2xl">{goal.description}</p>

                  <div className="space-y-4">
                    <div className="flex justify-between text-sm font-bold">
                      <span className="text-zinc-500 uppercase tracking-widest">Progress</span>
                      <span className="text-emerald-400">{goal.progress}%</span>
                    </div>
                    <div className="h-3 bg-zinc-950 rounded-full border border-zinc-800 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${goal.progress}%` }}
                        className="h-full bg-emerald-500"
                      />
                    </div>
                  </div>

                  {goal.is_completed && (
                    <div className="absolute top-4 right-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                      <Trophy className="h-3 w-3" />
                      Completed
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {editingGoal && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 z-50">
              <motion.form
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                onSubmit={handleSave}
                className="bg-zinc-950 border border-zinc-800 w-full max-w-lg p-8 rounded-3xl shadow-2xl"
              >
                <h2 className="text-2xl font-bold mb-6">
                  {editingGoal.id ? "Update Goal" : "Set Goal"}
                </h2>
                <div className="space-y-4">
                  <input
                    autoFocus
                    value={editingGoal.title}
                    onChange={(e) => setEditingGoal({ ...editingGoal, title: e.target.value })}
                    placeholder="Goal Title"
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 focus:outline-none focus:border-zinc-500 transition"
                  />
                  <textarea
                    value={editingGoal.description}
                    onChange={(e) => setEditingGoal({ ...editingGoal, description: e.target.value })}
                    placeholder="Describe your goal..."
                    rows={3}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 focus:outline-none focus:border-zinc-500 transition resize-none"
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1 block">Progress (%)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={editingGoal.progress}
                        onChange={(e) => setEditingGoal({ ...editingGoal, progress: parseInt(e.target.value) })}
                        className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-3 focus:outline-none focus:border-zinc-500 transition"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1 block">Target Date</label>
                      <input
                        type="date"
                        value={editingGoal.target_date || ""}
                        onChange={(e) => setEditingGoal({ ...editingGoal, target_date: e.target.value })}
                        className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-3 focus:outline-none focus:border-zinc-500 transition"
                      />
                    </div>
                  </div>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editingGoal.is_completed}
                      onChange={(e) => setEditingGoal({ ...editingGoal, is_completed: e.target.checked, progress: e.target.checked ? 100 : editingGoal.progress })}
                      className="h-5 w-5 rounded border-zinc-800 bg-zinc-900 text-emerald-500 focus:ring-0"
                    />
                    <span className="text-sm text-zinc-400">Mark as completed</span>
                  </label>
                </div>
                <div className="flex justify-end gap-3 mt-8">
                  <button
                    type="button"
                    onClick={() => setEditingGoal(null)}
                    className="px-6 py-2 text-zinc-400 hover:text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-white text-black px-6 py-2 rounded-xl font-bold hover:bg-zinc-200 transition"
                  >
                    Save Goal
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
