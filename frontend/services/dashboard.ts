import api from "./api";
import type { DashboardSummary } from "@/types/dashboard";

export const getDashboardSummary = async () => {
  const res = await api.get<DashboardSummary>("/dashboard/summary/");
  return res.data;
};
