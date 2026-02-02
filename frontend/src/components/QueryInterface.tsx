import React, { useState, useEffect } from 'react';
import { apiService } from '../api';
import './QueryInterface.css';

interface QueryInterfaceProps {
    onSubmit: (query: string) => void;
    isLoading?: boolean;
}

const QueryInterface: React.FC<QueryInterfaceProps> = ({ onSubmit, isLoading = false }) => {
    const [query, setQuery] = useState('');
    const [exampleQueries, setExampleQueries] = useState<string[]>([]);

    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const suggestions = await apiService.getSuggestedQueries();
                if (suggestions && suggestions.length > 0) {
                    setExampleQueries(suggestions);
                } else {
                    // Fallback
                    setExampleQueries([
                        "Which deep learning methods improved protein folding accuracy after 2020?",
                        "Show me all datasets used for drug discovery in the last five years",
                        "Which institutions are leading in quantum computing research?",
                        "What are the most cited papers on transformer architectures?"
                    ]);
                }
            } catch (error) {
                console.error('Failed to fetch suggestions:', error);
                setExampleQueries([
                    "Which deep learning methods improved protein folding accuracy after 2020?",
                    "Show me all datasets used for drug discovery in the last five years",
                    "Which institutions are leading in quantum computing research?",
                    "What are the most cited papers on transformer architectures?"
                ]);
            }
        };

        fetchSuggestions();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            onSubmit(query.trim());
        }
    };

    const handleExampleClick = (exampleQuery: string) => {
        setQuery(exampleQuery);
        onSubmit(exampleQuery);
    };

    return (
        <div className="query-interface">
            <form onSubmit={handleSubmit} className="query-form">
                <div className="input-wrapper">
                    <textarea
                        className="query-input"
                        placeholder="Ask about scientific research... (e.g., 'Which methods improved protein folding after 2020?')"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                        rows={3}
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={!query.trim() || isLoading}
                    >
                        {isLoading ? (
                            <svg className="spinner" width="20" height="20" viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.25" />
                                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
                            </svg>
                        ) : (
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        )}
                    </button>
                </div>
            </form>

            <div className="examples-section">
                <h3 className="examples-title">Example Queries (Based on Your Data)</h3>
                <div className="examples-grid">
                    {exampleQueries.map((example, idx) => (
                        <button
                            key={idx}
                            className="example-chip hover-lift"
                            onClick={() => handleExampleClick(example)}
                            disabled={isLoading}
                        >
                            {example}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default QueryInterface;
