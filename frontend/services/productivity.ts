import api from "./api";
import type { Note, Task, Goal } from "@/types/productivity";

// Notes
export const getNotes = async () => {
  const res = await api.get<Note[]>("/productivity/notes/");
  return res.data;
};

export const createNote = async (data: Partial<Note>) => {
  const res = await api.post<Note>("/productivity/notes/", data);
  return res.data;
};

export const updateNote = async (id: number, data: Partial<Note>) => {
  const res = await api.patch<Note>(`/productivity/notes/${id}/`, data);
  return res.data;
};

export const deleteNote = async (id: number) => {
  await api.delete(`/productivity/notes/${id}/`);
};

// Tasks
export const getTasks = async () => {
  const res = await api.get<Task[]>("/productivity/tasks/");
  return res.data;
};

export const createTask = async (data: Partial<Task>) => {
  const res = await api.post<Task>("/productivity/tasks/", data);
  return res.data;
};

export const updateTask = async (id: number, data: Partial<Task>) => {
  const res = await api.patch<Task>(`/productivity/tasks/${id}/`, data);
  return res.data;
};

export const deleteTask = async (id: number) => {
  await api.delete(`/productivity/tasks/${id}/`);
};

// Goals
export const getGoals = async () => {
  const res = await api.get<Goal[]>("/productivity/goals/");
  return res.data;
};

export const createGoal = async (data: Partial<Goal>) => {
  const res = await api.post<Goal>("/productivity/goals/", data);
  return res.data;
};

export const updateGoal = async (id: number, data: Partial<Goal>) => {
  const res = await api.patch<Goal>(`/productivity/goals/${id}/`, data);
  return res.data;
};

export const deleteGoal = async (id: number) => {
  await api.delete(`/productivity/goals/${id}/`);
};
