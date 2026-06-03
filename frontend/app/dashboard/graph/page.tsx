"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node as FlowNode,
  Edge as FlowEdge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import Sidebar from "@/components/layout/Sidebar";
import { getGraphData, getNodeDetail } from "@/services/graph";
import { useAuth } from "@/hooks/useAuth";
import type { GraphNode, GraphEdge, NodeDetail } from "@/types/graph";
import { motion, AnimatePresence } from "framer-motion";
import { X, Info, FileText } from "lucide-react";

const nodeColorMap: Record<string, string> = {
  person: "#93c5fd", // blue-300
  project: "#c084fc", // purple-400
  company: "#fb923c", // orange-400
  technology: "#4ade80", // green-400
  topic: "#94a3b8", // slate-400
  concept: "#f472b6", // pink-400
  other: "#d1d5db", // gray-300
};

export default function GraphPage() {
  const { token } = useAuth({ required: true });
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<NodeDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    const fetchData = async () => {
      try {
        const data = await getGraphData();
        
        const flowNodes: FlowNode[] = data.nodes.map((node, index) => ({
          id: node.id.toString(),
          data: { label: node.title, ...node },
          position: { 
            x: Math.cos(index) * 400 + 400, 
            y: Math.sin(index) * 400 + 400 
          },
          style: {
            background: nodeColorMap[node.node_type] || "#94a3b8",
            color: "#000",
            borderRadius: "12px",
            padding: "10px",
            fontSize: "12px",
            fontWeight: "bold",
            width: 150,
            textAlign: "center",
          },
        }));

        const flowEdges: FlowEdge[] = data.edges.map((edge) => ({
          id: `e-${edge.id}`,
          source: edge.source.toString(),
          target: edge.target.toString(),
          label: edge.relationship_type.replace("_", " "),
          style: { stroke: "#555" },
          labelStyle: { fill: "#888", fontSize: 10 },
        }));

        setNodes(flowNodes);
        setEdges(flowEdges);
      } catch (err) {
        console.error("Failed to fetch graph data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, setNodes, setEdges]);

  const onNodeClick = useCallback(async (_: any, node: FlowNode) => {
    try {
      const detail = await getNodeDetail(parseInt(node.id));
      setSelectedNode(detail);
    } catch (err) {
      console.error("Failed to fetch node detail", err);
    }
  }, []);

  if (!token) return null;

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <Sidebar />

      <main className="flex-1 relative flex flex-col">
        <div className="p-6 bg-black/50 backdrop-blur-md border-b border-zinc-800 z-10">
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge Graph</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Visualizing connections between entities across your documents.
          </p>
        </div>

        <div className="flex-1">
          {loading ? (
            <div className="h-full w-full flex items-center justify-center bg-zinc-950">
              <div className="text-zinc-500 animate-pulse flex flex-col items-center">
                <div className="h-12 w-12 border-4 border-zinc-800 border-t-zinc-400 rounded-full animate-spin mb-4" />
                Mapping Knowledge...
              </div>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
              colorMode="dark"
            >
              <Background color="#222" gap={20} />
              <Controls />
              <MiniMap 
                nodeStrokeColor={(n: any) => nodeColorMap[n.data.node_type] || "#eee"}
                nodeColor={(n: any) => nodeColorMap[n.data.node_type] || "#fff"}
                maskColor="rgb(0, 0, 0, 0.7)"
              />
            </ReactFlow>
          )}
        </div>

        <AnimatePresence>
          {selectedNode && (
            <motion.aside
              initial={{ x: 400 }}
              animate={{ x: 0 }}
              exit={{ x: 400 }}
              transition={{ type: "spring", damping: 20 }}
              className="absolute right-0 top-0 bottom-0 w-96 bg-zinc-950 border-l border-zinc-800 p-6 z-20 shadow-2xl overflow-y-auto"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div 
                    className="h-3 w-3 rounded-full" 
                    style={{ background: nodeColorMap[selectedNode.node_type] }} 
                  />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">
                    {selectedNode.node_type}
                  </span>
                </div>
                <button 
                  onClick={() => setSelectedNode(null)}
                  className="p-1 hover:bg-zinc-800 rounded transition"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <h2 className="text-2xl font-bold mb-4">{selectedNode.title}</h2>
              
              {selectedNode.description && (
                <div className="mb-8">
                  <div className="flex items-center gap-2 text-zinc-400 mb-2">
                    <Info className="h-4 w-4" />
                    <span className="text-xs font-semibold">Description</span>
                  </div>
                  <p className="text-sm text-zinc-300 leading-relaxed">
                    {selectedNode.description}
                  </p>
                </div>
              )}

              {selectedNode.source_documents.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 text-zinc-400 mb-3">
                    <FileText className="h-4 w-4" />
                    <span className="text-xs font-semibold">Sources</span>
                  </div>
                  <div className="space-y-2">
                    {selectedNode.source_documents.map(doc => (
                      <div 
                        key={doc.id}
                        className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition"
                      >
                        <FileText className="h-4 w-4 text-zinc-500" />
                        <span className="text-sm truncate">{doc.title}</span>
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
