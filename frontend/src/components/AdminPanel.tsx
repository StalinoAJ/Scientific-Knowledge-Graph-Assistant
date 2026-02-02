import React, { useState, useEffect } from 'react';
import { apiService } from '../api';
import './AdminPanel.css';

interface AdminPanelProps {
    onClose: () => void;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onClose }) => {
    const [health, setHealth] = useState<any>(null);
    const [ingestQuery, setIngestQuery] = useState('');
    const [maxResults, setMaxResults] = useState(10);
    const [isIngesting, setIsIngesting] = useState(false);
    const [ingestResult, setIngestResult] = useState<{ type: 'success' | 'error', message: string } | null>(null);

    // Delete state
    const [cleanupQuery, setCleanupQuery] = useState('');
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteResult, setDeleteResult] = useState<{ type: 'success' | 'error', message: string } | null>(null);

    // Initial health check
    useEffect(() => {
        checkHealth();
    }, []);

    const checkHealth = async () => {
        try {
            const status = await apiService.healthCheck();
            setHealth(status);
        } catch (error) {
            console.error('Health check failed', error);
            setHealth({ status: 'offline', services: { neo4j: 'down', ollama: 'down' } });
        }
    };

    const handleDelete = async (query?: string) => {
        if (!query && !window.confirm("ARE YOU SURE? This will delete ALL data in the graph!")) {
            return;
        }

        setIsDeleting(true);
        setDeleteResult(null);
        try {
            const response = await apiService.deleteData(query, true);
            setDeleteResult({
                type: 'success',
                message: response.message
            });
            if (query) setCleanupQuery('');
            checkHealth();
        } catch (err: any) {
            setDeleteResult({
                type: 'error',
                message: err.message || 'Deletion failed'
            });
        } finally {
            setIsDeleting(false);
        }
    };

    const handleIngest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!ingestQuery.trim()) return;

        setIsIngesting(true);
        setIngestResult(null);

        try {
            const response = await apiService.ingestPapers({
                query: ingestQuery,
                max_results_per_source: maxResults,
                sources: ['arxiv', 'semantic_scholar'] // Default sources
            });

            setIngestResult({
                type: 'success',
                message: `Successfully fetched ${response.papers_fetched} papers. Processing in background.`
            });
            setIngestQuery('');
        } catch (error) {
            setIngestResult({
                type: 'error',
                message: 'Ingestion failed. Please check the backend logs.'
            });
        } finally {
            setIsIngesting(false);
        }
    };

    return (
        <div className="admin-panel-overlay" onClick={(e) => {
            if (e.target === e.currentTarget) onClose();
        }}>
            <div className="admin-panel">
                <div className="admin-header">
                    <div className="admin-title">System Admin</div>
                    <button className="close-btn" onClick={onClose}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="admin-content">
                    {/* Health Status Section */}
                    <div className="admin-section">
                        <div className="section-title">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            System Status
                            <button className="refresh-btn" onClick={checkHealth} title="Refresh Status" style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                                ↻
                            </button>
                        </div>

                        <div className="status-grid">
                            <div className="status-card">
                                <div className={`status-indicator ${health?.services?.neo4j === 'up' ? 'healthy' : 'down'}`} />
                                <div>
                                    <div className="service-name">Graph Database (Neo4j)</div>
                                    <div className="service-status">{health?.services?.neo4j === 'up' ? 'Online' : 'Offline'}</div>
                                </div>
                            </div>

                            <div className="status-card">
                                <div className={`status-indicator ${health?.services?.ollama === 'up' ? 'healthy' : 'down'}`} />
                                <div>
                                    <div className="service-name">LLM Service (Ollama)</div>
                                    <div className="service-status">{health?.services?.ollama === 'up' ? 'Online' : 'Offline'}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Ingestion Section */}
                    <div className="admin-section">
                        <div className="section-title">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                            Ingest Data
                        </div>

                        <form onSubmit={handleIngest} className="ingest-form">
                            <div className="form-group">
                                <label className="form-label">Search Topic</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="e.g. Deep Learning, Protein Folding..."
                                    value={ingestQuery}
                                    onChange={(e) => setIngestQuery(e.target.value)}
                                    disabled={isIngesting}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Max Papers to Fetch</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={maxResults}
                                    onChange={(e) => setMaxResults(parseInt(e.target.value))}
                                    min={1}
                                    max={50}
                                    disabled={isIngesting}
                                />
                            </div>

                            <button type="submit" className="ingest-btn" disabled={!ingestQuery || isIngesting}>
                                {isIngesting ? 'Ingesting...' : 'Start Ingestion'}
                            </button>
                        </form>

                        {ingestResult && (
                            <div className={`ingest-result ${ingestResult.type}`}>
                                {ingestResult.message}
                            </div>
                        )}
                    </div>

                    {/* Data Management Section */}
                    <div className="admin-section">
                        <div className="section-title" style={{ color: '#ef4444' }}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Data Management
                        </div>

                        <div className="delete-actions" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div className="form-group">
                                <label className="form-label">Delete Specific Papers (Filtered)</label>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <input
                                        type="text"
                                        className="form-input"
                                        placeholder="Enter topic/title to delete..."
                                        value={cleanupQuery}
                                        onChange={(e) => setCleanupQuery(e.target.value)}
                                        disabled={isDeleting}
                                        style={{ flex: 1 }}
                                    />
                                    <button
                                        className="ingest-btn"
                                        style={{ background: '#f59e0b', marginTop: 0 }}
                                        onClick={() => handleDelete(cleanupQuery)}
                                        disabled={!cleanupQuery || isDeleting}
                                    >
                                        Delete Matches
                                    </button>
                                </div>
                                <div className="form-hint" style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                                    Deletes all papers (and their exclusive relationships) that contain this text.
                                </div>
                            </div>

                            <div className="form-group" style={{ borderTop: '1px solid rgba(239, 68, 68, 0.2)', paddingTop: '20px' }}>
                                <label className="form-label" style={{ color: '#ef4444' }}>Danger Zone</label>
                                <button
                                    className="ingest-btn"
                                    style={{ background: '#ef4444', width: '100%' }}
                                    onClick={() => handleDelete()}
                                    disabled={isDeleting}
                                >
                                    {isDeleting ? 'Deleting...' : 'DELETE ALL DATA'}
                                </button>
                                <div className="form-hint" style={{ fontSize: '12px', color: '#ef4444', marginTop: '4px', textAlign: 'center' }}>
                                    Warning: This will permanently wipe the entire database.
                                </div>
                            </div>
                        </div>

                        {deleteResult && (
                            <div className={`ingest-result ${deleteResult.type}`}>
                                {deleteResult.message}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminPanel;
