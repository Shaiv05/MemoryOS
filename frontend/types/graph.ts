export type NodeType =
  | "person"
  | "project"
  | "company"
  | "technology"
  | "topic"
  | "concept"
  | "other";

export type RelationshipType =
  | "works_on"
  | "uses"
  | "belongs_to"
  | "references"
  | "related_to";

export interface GraphNode {
  id: number;
  title: string;
  node_type: NodeType;
  description: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface GraphEdge {
  id: number;
  source: number;
  target: number;
  source_title: string;
  target_title: string;
  relationship_type: RelationshipType;
  description: string;
  weight: number;
  created_at: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface NodeDetail extends GraphNode {
  source_documents: { id: number; title: string }[];
}
