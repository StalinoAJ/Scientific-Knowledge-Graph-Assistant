import React, { useState, useEffect } from 'react';
import QueryInterface from './components/QueryInterface';
import AnswerDisplay from './components/AnswerDisplay';
import GraphViz from './visualizations/GraphViz';
import AdminPanel from './components/AdminPanel';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import { apiService } from './api';
import { QueryResponse, GraphData, Stats } from './types';
import './App.css';

const App: React.FC = () => {
    const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
    const [stats, setStats] = useState<Stats | null>(null);
    const [isQuerying, setIsQuerying] = useState(false);
    const [healthStatus, setHealthStatus] = useState<{ neo4j: string, ollama: string } | null>(null);
    const [selectedTab, setSelectedTab] = useState<'answer' | 'graph' | 'analytics'>('answer');
    const [highlightedNodes, setHighlightedNodes] = useState<string[]>([]);
    const [showAdmin, setShowAdmin] = useState(false);

    // Load initial graph data and stats
    useEffect(() => {
        loadGraphData();
        loadStats();
        checkHealth();
    }, []);

    const checkHealth = async () => {
        try {
            const health = await apiService.healthCheck();
            setHealthStatus(health.services);
        } catch (error) {
            console.error('Health check failed:', error);
        }
    };

    const loadGraphData = async () => {
        try {
            console.log('Loading graph data...');
            const data = await apiService.exportGraph(500);
            console.log('Graph data loaded:', data);
            console.log('Nodes:', data.nodes?.length, 'Edges:', data.edges?.length);
            setGraphData(data);
        } catch (error) {
            console.error('Failed to load graph data:', error);
            // Set empty data to prevent errors
            setGraphData({ nodes: [], edges: [] });
        }
    };

    const loadStats = async () => {
        try {
            const statsData = await apiService.getStats();
            setStats(statsData);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const handleQuery = async (query: string) => {
        setIsQuerying(true);
        setSelectedTab('answer');

        try {
            const response = await apiService.query(query);
            setQueryResponse(response);

            // Highlight relevant nodes in graph
            const relevantNodeIds = response.context.search_results?.map(r => r.node_id) || [];
            setHighlightedNodes(relevantNodeIds);

            // Refresh graph if we got new context
            if (response.context.nodes.length > 0) {
                setGraphData({
                    nodes: response.context.nodes,
                    edges: response.context.edges || [],
                });
            }
        } catch (error) {
            console.error('Query failed:', error);
            // Set error state
            setQueryResponse({
                query,
                answer: 'Failed to process query. Please make sure the backend is running and try again.',
                context: { search_results: [], nodes: [], edges: [] },
                citations: [],
            });
        } finally {
            setIsQuerying(false);
        }
    };

    const handleNodeClick = (nodeId: string) => {
        console.log('Node clicked:', nodeId);
        // Could fetch more details about the node here
    };

    return (
        <div className="app">
            {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}

            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <h1 className="app-title">
                        <span className="gradient-text">Scientific Knowledge Graph</span>
                        <span className="subtitle">AI-Powered Research Assistant</span>
                    </h1>
                    <div className="header-actions">
                        <button
                            className="admin-btn"
                            onClick={() => setShowAdmin(true)}
                            title="System Status & Ingestion"
                        >
                            Admin & Tools
                        </button>
                        {stats && (
                            <div className="stats-badge">
                                <span className="stat-item">{stats.nodes_by_type?.Paper || 0} papers</span>
                                <span className="stat-divider">•</span>
                                <span className="stat-item">{stats.total_relationships} connections</span>
                            </div>
                        )}
                        {healthStatus && (
                            <div className="health-indicators">
                                <div className={`health-dot ${healthStatus.neo4j === 'up' ? 'healthy' : 'unhealthy'}`} title="Neo4j"></div>
                                <div className={`health-dot ${healthStatus.ollama === 'up' ? 'healthy' : 'unhealthy'}`} title="Ollama"></div>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="app-main">
                <div className="content-container">
                    {/* Query Interface */}
                    <section className="query-section">
                        <QueryInterface onSubmit={handleQuery} isLoading={isQuerying} />
                    </section>

                    {/* Results Section */}
                    <section className="results-section">
                        <div className="results-tabs">
                            <button
                                className={`tab-btn ${selectedTab === 'answer' ? 'active' : ''}`}
                                onClick={() => setSelectedTab('answer')}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                                Answer
                            </button>
                            <button
                                className={`tab-btn ${selectedTab === 'graph' ? 'active' : ''}`}
                                onClick={() => setSelectedTab('graph')}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                </svg>
                                Knowledge Graph
                            </button>
                            <button
                                className={`tab-btn ${selectedTab === 'analytics' ? 'active' : ''}`}
                                onClick={() => setSelectedTab('analytics')}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                                Analytics
                            </button>
                        </div>

                        <div className="results-content">
                            {selectedTab === 'answer' ? (
                                <AnswerDisplay response={queryResponse} isLoading={isQuerying} />
                            ) : selectedTab === 'graph' ? (
                                <div className="graph-container">
                                    <GraphViz
                                        data={graphData}
                                        onNodeClick={handleNodeClick}
                                        highlightNodes={highlightedNodes}
                                    />
                                </div>
                            ) : (
                                <AnalyticsDashboard />
                            )}
                        </div>
                    </section>
                </div>
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <p>Powered by Llama 3.2, Neo4j, and Cytoscape.js • Zero-cost, open-source research assistant</p>
            </footer>
        </div>
    );
};

export default App;
