import api from "./api";
import type { GraphData, NodeDetail } from "@/types/graph";

export const getGraphData = async () => {
  const res = await api.get<GraphData>("/graph/data/");
  return res.data;
};

export const getNodeDetail = async (id: number) => {
  const res = await api.get<NodeDetail>(`/graph/nodes/${id}/`);
  return res.data;
};
