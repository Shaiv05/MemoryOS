export interface Note {
  id: number;
  title: string;
  content: string;
  related_documents: number[];
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "completed";
  priority: "low" | "medium" | "high";
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: number;
  title: string;
  description: string;
  status: "planned" | "in_progress" | "completed" | "paused";
  priority: "low" | "medium" | "high";
  target_date: string | null;
  deadline: string | null;
  progress: number;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}
