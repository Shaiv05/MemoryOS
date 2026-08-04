"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node as FlowNode,
  Edge as FlowEdge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import * as force from "d3-force";

import Sidebar from "@/components/layout/Sidebar";
import { getGraphData, getNodeDetail } from "@/services/graph";
import { useAuth } from "@/hooks/useAuth";
import type { NodeDetail, NodeType } from "@/types/graph";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Info,
  FileText,
  Search,
  Maximize2,
  RefreshCw,
  Layers,
  Sparkles,
  BookOpen,
  Filter,
} from "lucide-react";

const nodeColorMap: Record<NodeType, { bg: string; border: string; text: string; glow: string }> = {
  person: { bg: "#1e3a8a", border: "#3b82f6", text: "#93c5fd", glow: "rgba(59, 130, 246, 0.4)" },
  project: { bg: "#581c87", border: "#a855f7", text: "#e9d5ff", glow: "rgba(168, 85, 247, 0.4)" },
  company: { bg: "#7c2d12", border: "#f97316", text: "#ffedd5", glow: "rgba(249, 115, 22, 0.4)" },
  technology: { bg: "#064e3b", border: "#10b981", text: "#a7f3d0", glow: "rgba(16, 185, 129, 0.4)" },
  topic: { bg: "#1e293b", border: "#64748b", text: "#cbd5e1", glow: "rgba(100, 116, 139, 0.4)" },
  concept: { bg: "#831843", border: "#ec4899", text: "#fbcfe8", glow: "rgba(236, 72, 153, 0.4)" },
  other: { bg: "#134e4a", border: "#14b8a6", text: "#99f6e4", glow: "rgba(20, 184, 166, 0.4)" },
};

type LayoutMode = "force" | "radial" | "grid";

export default function GraphPage() {
  const { token } = useAuth({ required: true });
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);
  const [rawData, setRawData] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<NodeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>("all");
  const [layoutMode, setLayoutMode] = useState<LayoutMode>("force");
  const [hoveredNode, setHoveredNode] = useState<FlowNode | null>(null);

  const applyLayout = useCallback(
    (graphNodes: any[], graphEdges: any[], mode: LayoutMode) => {
      if (!graphNodes.length) return { nodes: [], edges: [] };

      const nodesCopy = graphNodes.map((n, idx) => ({
        id: n.id.toString(),
        x: Math.cos(idx) * 300,
        y: Math.sin(idx) * 300,
        raw: n,
      }));

      const edgesCopy = graphEdges.map((e) => ({
        source: e.source.toString(),
        target: e.target.toString(),
        raw: e,
      }));

      if (mode === "force") {
        const simulation = force
          .forceSimulation(nodesCopy as any)
          .force(
            "link",
            force.forceLink(edgesCopy as any).id((d: any) => d.id).distance(140)
          )
          .force("charge", force.forceManyBody().strength(-400))
          .force("center", force.forceCenter(400, 300))
          .force("collide", force.forceCollide(85))
          .stop();

        for (let i = 0; i < 200; ++i) simulation.tick();
      } else if (mode === "radial") {
        const count = nodesCopy.length;
        nodesCopy.forEach((node, i) => {
          const angle = (i / count) * 2 * Math.PI;
          const radius = 300 + (i % 2) * 80;
          node.x = 400 + radius * Math.cos(angle);
          node.y = 300 + radius * Math.sin(angle);
        });
      } else if (mode === "grid") {
        const cols = Math.ceil(Math.sqrt(nodesCopy.length));
        nodesCopy.forEach((node, i) => {
          const col = i % cols;
          const row = Math.floor(i / cols);
          node.x = col * 220 + 100;
          node.y = row * 160 + 100;
        });
      }

      const flowNodes: FlowNode[] = nodesCopy.map((n) => {
        const typeKey = (n.raw.node_type as NodeType) || "topic";
        const palette = nodeColorMap[typeKey] || nodeColorMap.topic;
        const isMatched =
          searchQuery.trim() === "" ||
          n.raw.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          n.raw.description?.toLowerCase().includes(searchQuery.toLowerCase());

        const isFilteredOut =
          selectedTypeFilter !== "all" && n.raw.node_type !== selectedTypeFilter;

        const opacity = isFilteredOut ? 0.15 : isMatched ? 1.0 : 0.25;

        return {
          id: n.id,
          data: { label: n.raw.title, ...n.raw },
          position: { x: n.x, y: n.y },
          style: {
            background: palette.bg,
            color: palette.text,
            border: `2px solid ${palette.border}`,
            borderRadius: "14px",
            padding: "10px 14px",
            fontSize: "12px",
            fontWeight: "600",
            width: 170,
            textAlign: "center",
            boxShadow: isMatched && searchQuery ? `0 0 20px ${palette.glow}` : `0 4px 12px rgba(0,0,0,0.5)`,
            opacity,
            transition: "all 0.3s ease",
            cursor: "pointer",
          },
        };
      });

      const flowEdges: FlowEdge[] = graphEdges.map((edge) => {
        const relLabel = edge.relationship_type.replace("_", " ");
        return {
          id: `e-${edge.id}`,
          source: edge.source.toString(),
          target: edge.target.toString(),
          label: relLabel,
          type: "smoothstep",
          animated: true,
          style: { stroke: "#475569", strokeWidth: 1.5 },
          labelStyle: { fill: "#94a3b8", fontSize: 10, fontWeight: 500 },
          labelBgStyle: { fill: "#0f172a", fillOpacity: 0.85, rx: 6, ry: 6 },
          labelBgPadding: [6, 4] as [number, number],
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: "#64748b",
            width: 14,
            height: 14,
          },
        };
      });

      return { nodes: flowNodes, edges: flowEdges };
    },
    [searchQuery, selectedTypeFilter]
  );

  const fetchGraphData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getGraphData();
      setRawData(data);
      const { nodes: fNodes, edges: fEdges } = applyLayout(data.nodes, data.edges, layoutMode);
      setNodes(fNodes);
      setEdges(fEdges);
    } catch (err) {
      console.error("Failed to fetch graph data", err);
    } finally {
      setLoading(false);
    }
  }, [applyLayout, layoutMode, setNodes, setEdges]);

  useEffect(() => {
    if (!token) return;
    fetchGraphData();
  }, [token, fetchGraphData]);

  useEffect(() => {
    if (rawData.nodes.length) {
      const { nodes: fNodes, edges: fEdges } = applyLayout(rawData.nodes, rawData.edges, layoutMode);
      setNodes(fNodes);
      setEdges(fEdges);
    }
  }, [searchQuery, selectedTypeFilter, layoutMode, rawData, applyLayout, setNodes, setEdges]);

  const onNodeClick = useCallback(async (_: React.MouseEvent, node: FlowNode) => {
    try {
      const detail = await getNodeDetail(parseInt(node.id));
      setSelectedNode(detail);
    } catch (err) {
      console.error("Failed to fetch node detail", err);
    }
  }, []);

  const onNodeMouseEnter = useCallback((_: React.MouseEvent, node: FlowNode) => {
    setHoveredNode(node);
  }, []);

  const onNodeMouseLeave = useCallback(() => {
    setHoveredNode(null);
  }, []);

  const uniqueNodeTypes = useMemo(() => {
    const types = new Set(rawData.nodes.map((n) => n.node_type));
    return Array.from(types);
  }, [rawData.nodes]);

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <Sidebar />

      <main className="flex-1 relative flex flex-col min-w-0">
        {/* Header Controls */}
        <div className="p-5 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800 z-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-purple-400" />
              Interactive Knowledge Graph
            </h1>
            <p className="text-xs text-zinc-400 mt-1">
              Visualizing entities, relationships, and document/note connections.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Highlight nodes..."
                className="pl-9 pr-4 py-2 bg-black border border-zinc-800 rounded-lg text-xs text-white placeholder-zinc-500 outline-none focus:border-purple-500 transition-all w-48"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2.5 text-zinc-500 hover:text-white"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Layout Mode Selector */}
            <div className="flex rounded-lg border border-zinc-800 bg-black p-1 text-xs">
              {(["force", "radial", "grid"] as LayoutMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setLayoutMode(mode)}
                  className={`px-3 py-1 rounded capitalize font-medium transition-all ${
                    layoutMode === mode
                      ? "bg-purple-600 text-white shadow"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>

            <button
              onClick={fetchGraphData}
              className="p-2 rounded-lg border border-zinc-800 bg-black text-zinc-400 hover:text-white hover:border-zinc-700 transition"
              title="Refresh Graph"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="px-5 py-2.5 bg-zinc-900/60 border-b border-zinc-800/80 z-10 flex items-center gap-2 overflow-x-auto text-xs">
          <Filter size={13} className="text-zinc-500 shrink-0" />
          <span className="text-zinc-500 font-medium mr-1">Filter Type:</span>
          <button
            onClick={() => setSelectedTypeFilter("all")}
            className={`px-2.5 py-1 rounded-md font-medium transition ${
              selectedTypeFilter === "all"
                ? "bg-zinc-100 text-black font-semibold"
                : "bg-zinc-950 border border-zinc-800 text-zinc-400 hover:text-white"
            }`}
          >
            All ({rawData.nodes.length})
          </button>
          {uniqueNodeTypes.map((type) => {
            const count = rawData.nodes.filter((n) => n.node_type === type).length;
            const color = nodeColorMap[type as NodeType] || nodeColorMap.topic;
            return (
              <button
                key={type}
                onClick={() => setSelectedTypeFilter(type)}
                className={`px-2.5 py-1 rounded-md font-medium border flex items-center gap-1.5 transition ${
                  selectedTypeFilter === type
                    ? "bg-zinc-800 text-white border-zinc-600"
                    : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-white"
                }`}
              >
                <span className="h-2 w-2 rounded-full" style={{ background: color.border }} />
                <span className="capitalize">{type}</span>
                <span className="text-[10px] opacity-70">({count})</span>
              </button>
            );
          })}
        </div>

        {/* Graph Canvas */}
        <div className="flex-1 relative">
          {loading ? (
            <div className="h-full w-full flex items-center justify-center bg-zinc-950">
              <div className="text-zinc-400 animate-pulse flex flex-col items-center">
                <div className="h-10 w-10 border-4 border-zinc-800 border-t-purple-500 rounded-full animate-spin mb-4" />
                Simulating Knowledge Physics...
              </div>
            </div>
          ) : rawData.nodes.length === 0 ? (
            <div className="h-full w-full flex flex-col items-center justify-center bg-zinc-950 p-8 text-center">
              <Layers className="h-12 w-12 text-zinc-600 mb-3" />
              <h3 className="text-lg font-semibold text-zinc-300">No Knowledge Graph Nodes Yet</h3>
              <p className="text-sm text-zinc-500 max-w-md mt-1">
                Upload documents or notes to extract entity nodes and relationships automatically.
              </p>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              onNodeMouseEnter={onNodeMouseEnter}
              onNodeMouseLeave={onNodeMouseLeave}
              fitView
              colorMode="dark"
            >
              <Background color="#1e293b" gap={24} size={1} />
              <Controls />
              <MiniMap
                nodeStrokeColor={(n: FlowNode) =>
                  nodeColorMap[n.data?.node_type as NodeType]?.border || "#64748b"
                }
                nodeColor={(n: FlowNode) =>
                  nodeColorMap[n.data?.node_type as NodeType]?.bg || "#1e293b"
                }
                maskColor="rgba(0, 0, 0, 0.85)"
              />
            </ReactFlow>
          )}

          {/* Hover Tooltip Overlay */}
          <AnimatePresence>
            {hoveredNode && (
              <motion.div
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="pointer-events-none absolute bottom-6 left-6 z-30 rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 backdrop-blur-md shadow-2xl max-w-xs"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{
                      background:
                        nodeColorMap[hoveredNode.data?.node_type as NodeType]?.border || "#94a3b8",
                    }}
                  />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">
                    {hoveredNode.data?.node_type as string}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white">{hoveredNode.data?.title as string}</h4>
                {Boolean(hoveredNode.data?.description) && (
                  <p className="text-xs text-zinc-300 mt-1 line-clamp-2 leading-relaxed">
                    {String(hoveredNode.data?.description)}
                  </p>
                )}
                <div className="mt-2.5 flex items-center gap-3 text-[11px] text-zinc-500 border-t border-zinc-900 pt-2">
                  <span>Docs: {(hoveredNode.data?.source_documents as any[])?.length || 0}</span>
                  <span>Notes: {(hoveredNode.data?.notes as any[])?.length || 0}</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Selected Node Details Drawer */}
        <AnimatePresence>
          {selectedNode && (
            <motion.aside
              initial={{ x: 420 }}
              animate={{ x: 0 }}
              exit={{ x: 420 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="absolute right-0 top-0 bottom-0 w-96 bg-zinc-950/95 border-l border-zinc-800/80 p-6 z-30 shadow-2xl backdrop-blur-lg overflow-y-auto"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-2.5">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{
                      background: nodeColorMap[selectedNode.node_type]?.border || "#94a3b8",
                    }}
                  />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">
                    {selectedNode.node_type} Entity
                  </span>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <h2 className="text-2xl font-bold text-white mb-4">{selectedNode.title}</h2>

              {selectedNode.description && (
                <div className="mb-6 rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
                  <div className="flex items-center gap-2 text-zinc-400 mb-2">
                    <Info className="h-4 w-4" />
                    <span className="text-xs font-semibold">Description</span>
                  </div>
                  <p className="text-xs text-zinc-300 leading-relaxed">
                    {selectedNode.description}
                  </p>
                </div>
              )}

              {/* Source Documents Grouping */}
              {selectedNode.source_documents && selectedNode.source_documents.length > 0 && (
                <div className="mb-6">
                  <div className="flex items-center gap-2 text-zinc-400 mb-3">
                    <FileText className="h-4 w-4 text-purple-400" />
                    <span className="text-xs font-semibold text-zinc-200">Linked Documents ({selectedNode.source_documents.length})</span>
                  </div>
                  <div className="space-y-2">
                    {selectedNode.source_documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between gap-3 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 transition"
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <FileText className="h-4 w-4 shrink-0 text-zinc-400" />
                          <span className="text-xs font-medium text-zinc-200 truncate">{doc.title}</span>
                        </div>
                        {doc.file_type && (
                          <span className="rounded bg-zinc-800 px-2 py-0.5 text-[9px] uppercase font-bold text-zinc-400">
                            {doc.file_type}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Related Notes Grouping */}
              {selectedNode.notes && selectedNode.notes.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 text-zinc-400 mb-3">
                    <BookOpen className="h-4 w-4 text-emerald-400" />
                    <span className="text-xs font-semibold text-zinc-200">Linked Productivity Notes ({selectedNode.notes.length})</span>
                  </div>
                  <div className="space-y-2">
                    {selectedNode.notes.map((note) => (
                      <div
                        key={note.id}
                        className="flex items-center gap-2.5 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 transition"
                      >
                        <BookOpen className="h-4 w-4 shrink-0 text-emerald-400" />
                        <span className="text-xs font-medium text-zinc-200 truncate">{note.title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.aside>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
