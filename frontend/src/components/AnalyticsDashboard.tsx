import React, { useState, useEffect } from 'react';
import { apiService } from '../api';
import './AnalyticsDashboard.css';

interface TrendData {
    granularity: string;
    time_window_days: number;
    data: Record<string, number>;
}

interface MethodTrend {
    name: string;
    total_papers: number;
    timeline: Record<string, number>;
}

interface EmergingTopic {
    topic: string;
    recent_papers: number;
    earlier_papers: number;
    growth_rate: number;
}

interface AuthorProductivity {
    name: string;
    total_papers: number;
    by_year: Record<string, number>;
}

const AnalyticsDashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'trends' | 'clusters' | 'explore'>('trends');
    const [publicationTrends, setPublicationTrends] = useState<TrendData | null>(null);
    const [methodTrends, setMethodTrends] = useState<MethodTrend[]>([]);
    const [emergingTopics, setEmergingTopics] = useState<EmergingTopic[]>([]);
    const [topAuthors, setTopAuthors] = useState<AuthorProductivity[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Exploration state
    const [searchMethod, setSearchMethod] = useState('');
    const [searchAuthor, setSearchAuthor] = useState('');
    const [explorationResults, setExplorationResults] = useState<any>(null);

    useEffect(() => {
        if (activeTab === 'trends') {
            loadTrendData();
        }
    }, [activeTab]);

    const loadTrendData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [pubTrends, methTrends, emerging, authors] = await Promise.all([
                fetch('http://localhost:8000/analytics/trends/publications').then(r => r.json()),
                fetch('http://localhost:8000/analytics/trends/methods').then(r => r.json()),
                fetch('http://localhost:8000/analytics/trends/emerging').then(r => r.json()),
                fetch('http://localhost:8000/analytics/trends/authors').then(r => r.json()),
            ]);

            setPublicationTrends(pubTrends);
            setMethodTrends(methTrends.top_methods || []);
            setEmergingTopics(emerging.emerging_topics || []);
            setTopAuthors(authors.top_authors || []);
        } catch (err) {
            setError('Failed to load analytics data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const searchByMethod = async () => {
        if (!searchMethod.trim()) return;
        setLoading(true);
        try {
            const result = await fetch(`http://localhost:8000/explore/method/${encodeURIComponent(searchMethod)}`).then(r => r.json());
            setExplorationResults({ type: 'method', data: result });
        } catch (err) {
            setError('Failed to search by method');
        } finally {
            setLoading(false);
        }
    };

    const searchByAuthor = async () => {
        if (!searchAuthor.trim()) return;
        setLoading(true);
        try {
            const result = await fetch(`http://localhost:8000/explore/author/${encodeURIComponent(searchAuthor)}`).then(r => r.json());
            setExplorationResults({ type: 'author', data: result });
        } catch (err) {
            setError('Failed to search by author');
        } finally {
            setLoading(false);
        }
    };

    const renderTrendsTab = () => (
        <div className="analytics-section">
            <h2 className="section-title gradient-text">Research Trends</h2>

            {/* Publication Volume */}
            <div className="trend-card">
                <h3>Publication Volume Over Time</h3>
                {publicationTrends && publicationTrends.data && Object.keys(publicationTrends.data).length > 0 ? (
                    <div className="bar-chart">
                        {Object.entries(publicationTrends.data).slice(-12).map(([period, count]) => (
                            <div key={period} className="bar-item">
                                <div
                                    className="bar"
                                    style={{ height: `${Math.min(100, (count as number) * 10)}%` }}
                                    title={`${period}: ${count} papers`}
                                />
                                <span className="bar-label">{period.slice(-2)}</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-data">No publication data available</p>
                )}
            </div>

            {/* Trending Methods */}
            <div className="trend-card">
                <h3>Trending Methods</h3>
                {methodTrends.length > 0 ? (
                    <div className="method-list">
                        {methodTrends.slice(0, 5).map((method, idx) => (
                            <div key={idx} className="method-item hover-lift">
                                <span className="method-rank">{idx + 1}</span>
                                <span className="method-name">{method.name}</span>
                                <span className="method-count">{method.total_papers} papers</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-data">No method data available</p>
                )}
            </div>

            {/* Emerging Topics */}
            <div className="trend-card">
                <h3>Emerging Topics</h3>
                {emergingTopics.length > 0 ? (
                    <div className="topics-grid">
                        {emergingTopics.slice(0, 6).map((topic, idx) => (
                            <div key={idx} className="topic-chip">
                                <span className="topic-name">{topic.topic}</span>
                                <span className="topic-growth">+{topic.growth_rate}%</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-data">No emerging topics detected</p>
                )}
            </div>

            {/* Top Authors */}
            <div className="trend-card">
                <h3>Most Productive Authors</h3>
                {topAuthors.length > 0 ? (
                    <div className="author-list">
                        {topAuthors.slice(0, 5).map((author, idx) => (
                            <div key={idx} className="author-item">
                                <span className="author-rank">{idx + 1}</span>
                                <span className="author-name">{author.name}</span>
                                <span className="author-papers">{author.total_papers} papers</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-data">No author data available</p>
                )}
            </div>
        </div>
    );

    const renderClustersTab = () => (
        <div className="analytics-section">
            <h2 className="section-title gradient-text">Research Clusters</h2>
            <div className="cluster-info">
                <p>Research clusters help identify communities of researchers working on related topics.</p>
                <button
                    className="load-btn"
                    onClick={async () => {
                        setLoading(true);
                        try {
                            const landscape = await fetch('http://localhost:8000/analytics/landscape').then(r => r.json());
                            setExplorationResults({ type: 'landscape', data: landscape });
                        } catch (err) {
                            setError('Failed to load landscape');
                        } finally {
                            setLoading(false);
                        }
                    }}
                >
                    Load Research Landscape
                </button>
            </div>

            {explorationResults?.type === 'landscape' && (
                <div className="landscape-results">
                    <div className="landscape-card">
                        <h4>Topic Distribution</h4>
                        {explorationResults.data.topic_distribution?.top_topics?.slice(0, 5).map((topic: any, idx: number) => (
                            <div key={idx} className="topic-row">
                                <span>{topic.category}</span>
                                <span className="topic-count">{topic.paper_count} papers</span>
                            </div>
                        ))}
                    </div>

                    <div className="landscape-card">
                        <h4>Author Communities</h4>
                        <p>{explorationResults.data.author_communities?.total_communities || 0} communities found</p>
                    </div>
                </div>
            )}
        </div>
    );

    const renderExploreTab = () => (
        <div className="analytics-section">
            <h2 className="section-title gradient-text">Explore Research</h2>

            {/* Search by Method */}
            <div className="explore-card">
                <h3>Search by Method</h3>
                <div className="search-row">
                    <input
                        type="text"
                        placeholder="e.g., Transformer, CNN, BERT..."
                        value={searchMethod}
                        onChange={(e) => setSearchMethod(e.target.value)}
                        className="search-input"
                    />
                    <button onClick={searchByMethod} className="search-btn">Search</button>
                </div>
            </div>

            {/* Search by Author */}
            <div className="explore-card">
                <h3>Find Author Network</h3>
                <div className="search-row">
                    <input
                        type="text"
                        placeholder="Author name..."
                        value={searchAuthor}
                        onChange={(e) => setSearchAuthor(e.target.value)}
                        className="search-input"
                    />
                    <button onClick={searchByAuthor} className="search-btn">Find</button>
                </div>
            </div>

            {/* Results */}
            {explorationResults && explorationResults.type !== 'landscape' && (
                <div className="exploration-results">
                    <h3>Results</h3>
                    {explorationResults.type === 'method' && explorationResults.data.papers && (
                        <div className="papers-list">
                            {explorationResults.data.papers.slice(0, 10).map((paper: any, idx: number) => (
                                <div key={idx} className="paper-result">
                                    <span className="paper-title">{paper.title}</span>
                                    <span className="paper-meta">{paper.date} • {paper.authors?.slice(0, 2).join(', ')}</span>
                                </div>
                            ))}
                        </div>
                    )}
                    {explorationResults.type === 'author' && explorationResults.data.network && (
                        <div className="network-list">
                            <p>{explorationResults.data.total_collaborators} collaborators found</p>
                            {explorationResults.data.network.slice(0, 10).map((collab: any, idx: number) => (
                                <div key={idx} className="collab-item">
                                    <span>{collab.collaborator}</span>
                                    <span className="distance">Distance: {collab.distance}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    return (
        <div className="analytics-dashboard">
            <div className="analytics-tabs">
                <button
                    className={`tab-btn ${activeTab === 'trends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('trends')}
                >
                    📈 Trends
                </button>
                <button
                    className={`tab-btn ${activeTab === 'clusters' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clusters')}
                >
                    🔗 Clusters
                </button>
                <button
                    className={`tab-btn ${activeTab === 'explore' ? 'active' : ''}`}
                    onClick={() => setActiveTab('explore')}
                >
                    🔍 Explore
                </button>
            </div>

            {loading && <div className="loading-overlay">Loading...</div>}
            {error && <div className="error-message">{error}</div>}

            <div className="analytics-content">
                {activeTab === 'trends' && renderTrendsTab()}
                {activeTab === 'clusters' && renderClustersTab()}
                {activeTab === 'explore' && renderExploreTab()}
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
