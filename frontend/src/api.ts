import axios from 'axios';
import { QueryResponse, Stats, IngestRequest, IngestResponse, GraphData, Paper } from './types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    // Health check
    async healthCheck() {
        const response = await api.get('/health');
        return response.data;
    },

    // Query the knowledge graph
    async query(query: string) {
        const response = await api.post<QueryResponse>('/query', { query });
        return response.data;
    },

    // Get graph statistics
    async getStats() {
        const response = await api.get<Stats>('/stats');
        return response.data;
    },

    // Ingest papers
    async ingestPapers(request: IngestRequest) {
        const response = await api.post<IngestResponse>('/ingest', request);
        return response.data;
    },

    // Get paper details
    async getPaper(paperId: string) {
        const response = await api.get<Paper>(`/paper/${paperId}`);
        return response.data;
    },

    // Export graph for visualization
    async exportGraph(maxNodes: number = 500) {
        const response = await api.get<GraphData>('/graph/export', {
            params: { max_nodes: maxNodes },
        });
        return response.data;
    },

    // Get suggested queries
    async getSuggestedQueries() {
        const response = await api.get<string[]>('/queries/suggested');
        return response.data;
    },

    // Delete data query
    async deleteData(query?: string, confirm: boolean = true) {
        const response = await api.post('/admin/delete', { query, confirm });
        return response.data;
    }
};
