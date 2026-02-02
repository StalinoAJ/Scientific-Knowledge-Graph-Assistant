export interface Paper {
    node_id: string;
    title: string;
    abstract: string;
    authors: string[];
    publication_date?: string;
    venue?: string;
    url?: string;
    categories: string[];
    source: string;
}

export interface GraphNode {
    id: string;
    type: string;
    title?: string;
    name?: string;
    properties?: Record<string, any>;
}

export interface GraphEdge {
    source: string;
    target: string;
    type: string;
}

export interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

export interface QueryResponse {
    query: string;
    answer: string;
    context: {
        search_results: SearchResult[];
        nodes: GraphNode[];
        edges: GraphEdge[];
    };
    citations: string[];
}

export interface SearchResult {
    node_id: string;
    title: string;
    abstract: string;
    similarity: number;
}

export interface Stats {
    total_nodes: number;
    total_relationships: number;
    nodes_by_type: Record<string, number>;
    relationships_by_type: Record<string, number>;
}

export interface IngestRequest {
    query: string;
    max_results_per_source?: number;
    sources?: string[];
}

export interface IngestResponse {
    status: string;
    papers_fetched: number;
    papers_added: number;
    message: string;
}
