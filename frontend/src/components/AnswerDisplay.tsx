import React from 'react';
import { QueryResponse } from '../types';
import './AnswerDisplay.css';

interface AnswerDisplayProps {
    response: QueryResponse | null;
    isLoading?: boolean;
}

const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ response, isLoading }) => {
    if (isLoading) {
        return (
            <div className="answer-display">
                <div className="loading-skeleton">
                    <div className="skeleton-line" style={{ width: '90%' }}></div>
                    <div className="skeleton-line" style={{ width: '85%' }}></div>
                    <div className="skeleton-line" style={{ width: '80%' }}></div>
                </div>
            </div>
        );
    }

    if (!response) {
        return (
            <div className="answer-display empty-state">
                <div className="empty-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                </div>
                <p>Ask a question about scientific research to get started</p>
            </div>
        );
    }

    return (
        <div className="answer-display fade-in">
            <div className="query-echo">
                <strong>Q:</strong> {response.query}
            </div>

            <div className="answer-content">
                <h3 className="answer-heading">Answer</h3>
                <div className="answer-text">
                    {response.answer.split('\n').map((line, idx) => (
                        <p key={idx}>{line}</p>
                    ))}
                </div>
            </div>

            {response.context?.search_results && response.context.search_results.length > 0 && (
                <div className="sources-section">
                    <h3 className="sources-heading">Top Relevant Papers</h3>
                    <div className="sources-list">
                        {response.context.search_results.slice(0, 5).map((result, idx) => (
                            <div key={result.node_id} className="source-card hover-lift">
                                <div className="source-header">
                                    <span className="source-number">{idx + 1}</span>
                                    <div className="source-meta">
                                        <span className="source-id">{result.node_id}</span>
                                        <span className="similarity-badge">
                                            {(result.similarity * 100).toFixed(0)}% match
                                        </span>
                                    </div>
                                </div>
                                <h4 className="source-title">{result.title}</h4>
                                <p className="source-abstract">
                                    {result.abstract.substring(0, 150)}...
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {response.context?.nodes && response.context.nodes.length > 0 && (
                <div className="graph-summary">
                    <h3 className="summary-heading">Knowledge Graph Context</h3>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-value">{response.context.nodes.length}</div>
                            <div className="stat-label">Nodes Retrieved</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{response.context.edges?.length || 0}</div>
                            <div className="stat-label">Relationships</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{response.citations.length}</div>
                            <div className="stat-label">Citations</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnswerDisplay;
