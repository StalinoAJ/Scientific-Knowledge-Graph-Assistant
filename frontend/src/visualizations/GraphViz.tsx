import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';
import cola from 'cytoscape-cola';
import { GraphData } from '../types';
import './GraphViz.css';

// Register layout
cytoscape.use(cola);

interface GraphVizProps {
    data: GraphData;
    onNodeClick?: (nodeId: string) => void;
    highlightNodes?: string[];
}

const GraphViz: React.FC<GraphVizProps> = ({ data, onNodeClick, highlightNodes = [] }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<Core | null>(null);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [visibleNodeTypes, setVisibleNodeTypes] = useState<Set<string>>(
        new Set(['Paper', 'Author', 'Method', 'Dataset'])
    );
    const [layoutType, setLayoutType] = useState<'cola' | 'circle' | 'grid'>('cola');
    const [nodeTooltip, setNodeTooltip] = useState<{ x: number; y: number; content: any } | null>(null);

    // Node type colors
    const nodeColors: Record<string, string> = {
        Paper: '#3b82f6',
        Author: '#8b5cf6',
        Institution: '#ec4899',
        Method: '#10b981',
        Dataset: '#f59e0b',
        Result: '#ef4444',
    };

    // Count nodes by type
    const nodeCounts = data.nodes.reduce((acc, node) => {
        acc[node.type] = (acc[node.type] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    useEffect(() => {
        console.log('GraphViz useEffect triggered');
        console.log('Data:', data);

        if (!containerRef.current) {
            console.warn('Container ref is null');
            return;
        }

        if (!data.nodes || data.nodes.length === 0) {
            console.warn('No nodes in data');
            return;
        }

        // Filter nodes by type and search term
        const filteredNodes = data.nodes.filter(node => {
            const matchesType = visibleNodeTypes.has(node.type);
            const matchesSearch = !searchTerm ||
                (node.title?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (node.name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (node.id?.toLowerCase().includes(searchTerm.toLowerCase()));
            return matchesType && matchesSearch;
        });

        // Create a Set of visible node IDs
        const visibleNodeIds = new Set(filteredNodes.map(node => node.id));

        // Filter edges to only include those between visible nodes
        const filteredEdges = data.edges.filter(edge => {
            return visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target);
        });

        console.log(`Filtered: ${filteredNodes.length} nodes, ${filteredEdges.length} edges`);

        // Convert to Cytoscape format
        const elements: ElementDefinition[] = [
            ...filteredNodes.map(node => ({
                data: {
                    id: node.id,
                    label: node.title || node.name || node.id.split(':').pop() || node.id,
                    type: node.type,
                    color: nodeColors[node.type] || '#64748b',
                    fullData: node,
                },
            })),
            ...filteredEdges.map((edge, idx) => ({
                data: {
                    id: `edge-${idx}`,
                    source: edge.source,
                    target: edge.target,
                    label: edge.type.replace(/_/g, ' '),
                },
            })),
        ];

        // Destroy existing instance
        if (cyRef.current) {
            cyRef.current.destroy();
        }

        // Initialize Cytoscape
        const cy = cytoscape({
            container: containerRef.current,
            elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#f1f5f9',
                        'font-size': '10px',
                        'font-weight': 600,
                        'text-outline-color': '#0a0e1a',
                        'text-outline-width': 2,
                        'width': 35,
                        'height': 35,
                        'overlay-padding': '4px',
                        'z-index': 10,
                        'text-wrap': 'ellipsis',
                        'text-max-width': '80px',
                    } as any,
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 3,
                        'border-color': '#3b82f6',
                        'border-opacity': 1,
                    },
                },
                {
                    selector: 'node.highlighted',
                    style: {
                        'border-width': 4,
                        'border-color': '#8b5cf6',
                        'background-color': '#8b5cf6',
                        'border-opacity': 1,
                        'width': 45,
                        'height': 45,
                    },
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 1.5,
                        'line-color': '#334155',
                        'target-arrow-color': '#334155',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': '',  // Hide labels by default for cleaner view
                        'font-size': '9px',
                        'color': '#64748b',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -8,
                        'arrow-scale': 0.8,
                    } as any,
                },
                {
                    selector: 'edge.highlighted',
                    style: {
                        'line-color': '#8b5cf6',
                        'target-arrow-color': '#8b5cf6',
                        'width': 2.5,
                        'label': 'data(label)',
                    },
                },
            ],
            layout: getLayoutConfig(layoutType),
            minZoom: 0.2,
            maxZoom: 4,
            wheelSensitivity: 0.15,
        });

        // Event handlers
        cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            const nodeId = node.data('id');
            setSelectedNode(nodeId);

            // Highlight connected nodes and edges
            cy.elements().removeClass('highlighted');
            node.addClass('highlighted');
            node.connectedEdges().addClass('highlighted');
            node.neighborhood().addClass('highlighted');

            if (onNodeClick) {
                onNodeClick(nodeId);
            }
        });

        // Hover tooltip
        cy.on('mouseover', 'node', (evt) => {
            const node = evt.target;
            const renderedPosition = node.renderedPosition();
            const nodeData = node.data('fullData');

            setNodeTooltip({
                x: renderedPosition.x,
                y: renderedPosition.y - 50,
                content: nodeData,
            });
        });

        cy.on('mouseout', 'node', () => {
            setNodeTooltip(null);
        });

        cyRef.current = cy;

        return () => {
            cy.destroy();
        };
    }, [data, visibleNodeTypes, searchTerm, layoutType, onNodeClick]);

    // Highlight effect
    useEffect(() => {
        if (!cyRef.current) return;
        const cy = cyRef.current;

        cy.elements().removeClass('highlighted');

        if (highlightNodes.length > 0) {
            highlightNodes.forEach(nodeId => {
                const node = cy.getElementById(nodeId);
                node.addClass('highlighted');
                node.connectedEdges().addClass('highlighted');
            });

            const highlightedElements = cy.elements('.highlighted');
            if (highlightedElements.length > 0) {
                cy.animate({ fit: { eles: highlightedElements, padding: 50 }, duration: 500 });
            }
        }
    }, [highlightNodes]);

    const getLayoutConfig = (type: string) => {
        const configs = {
            cola: {
                name: 'cola',
                animate: true,
                randomize: false,
                maxSimulationTime: 2000,
                nodeSpacing: 60,
                edgeLength: 120,
                fit: true,
                padding: 30,
            },
            circle: {
                name: 'circle',
                animate: true,
                animationDuration: 500,
                fit: true,
                padding: 30,
            },
            grid: {
                name: 'grid',
                animate: true,
                animationDuration: 500,
                fit: true,
                padding: 30,
                rows: Math.ceil(Math.sqrt(data.nodes.length)),
            },
        };
        return configs[type as keyof typeof configs] as any;
    };

    const handleResetView = () => {
        cyRef.current?.fit(undefined, 30);
        cyRef.current?.elements().removeClass('highlighted');
        setSelectedNode(null);
    };

    const handleZoomIn = () => {
        cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
    };

    const handleZoomOut = () => {
        cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
    };

    const toggleNodeType = (type: string) => {
        const newTypes = new Set(visibleNodeTypes);
        if (newTypes.has(type)) {
            newTypes.delete(type);
        } else {
            newTypes.add(type);
        }
        setVisibleNodeTypes(newTypes);
    };

    const handleRelayout = () => {
        if (cyRef.current) {
            const layout = cyRef.current.layout(getLayoutConfig(layoutType));
            layout.run();
        }
    };

    return (
        <div className="graph-viz-container">
            <div ref={containerRef} className="graph-canvas" />

            {/* Toolbar */}
            <div className="graph-toolbar">
                <input
                    type="text"
                    className="search-box"
                    placeholder="Search nodes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />

                <div className="filter-panel">
                    <div className="filter-title">Node Types</div>
                    <div className="filter-options">
                        {Object.entries(nodeCounts).map(([type, count]) => (
                            <div
                                key={type}
                                className="filter-option"
                                onClick={() => toggleNodeType(type)}
                            >
                                <div className={`filter-checkbox ${visibleNodeTypes.has(type) ? 'checked' : ''}`}>
                                    {visibleNodeTypes.has(type) && (
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                                <div
                                    className="legend-dot"
                                    style={{ background: nodeColors[type] || '#64748b' }}
                                />
                                <span className="filter-label">{type}</span>
                                <span className="filter-count">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="layout-controls">
                    <button
                        className={`layout-btn ${layoutType === 'cola' ? 'active' : ''}`}
                        onClick={() => setLayoutType('cola')}
                    >
                        Force
                    </button>
                    <button
                        className={`layout-btn ${layoutType === 'circle' ? 'active' : ''}`}
                        onClick={() => setLayoutType('circle')}
                    >
                        Circle
                    </button>
                    <button
                        className={`layout-btn ${layoutType === 'grid' ? 'active' : ''}`}
                        onClick={() => setLayoutType('grid')}
                    >
                        Grid
                    </button>
                </div>
            </div>

            {/* Controls */}
            <div className="graph-controls">
                <button onClick={handleZoomIn} className="control-btn" title="Zoom In">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                    </svg>
                </button>
                <button onClick={handleZoomOut} className="control-btn" title="Zoom Out">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                    </svg>
                </button>
                <button onClick={handleResetView} className="control-btn" title="Reset View">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    </svg>
                </button>
                <button onClick={handleRelayout} className="control-btn" title="Re-layout">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                </button>
            </div>

            {/* Stats Panel */}
            <div className="stats-panel">
                <div className="stat-item">
                    <div className="stat-label">Nodes</div>
                    <div className="stat-value">{data.nodes.filter(n => visibleNodeTypes.has(n.type)).length}</div>
                </div>
                <div className="stat-item">
                    <div className="stat-label">Edges</div>
                    <div className="stat-value">{data.edges.length}</div>
                </div>
            </div>

            {/* Node Tooltip */}
            {nodeTooltip && (
                <div
                    className="node-tooltip"
                    style={{
                        left: nodeTooltip.x + 20,
                        top: nodeTooltip.y,
                    }}
                >
                    <div className="tooltip-type">{nodeTooltip.content.type}</div>
                    <div className="tooltip-title">
                        {nodeTooltip.content.title || nodeTooltip.content.name || nodeTooltip.content.id}
                    </div>
                </div>
            )}
        </div>
    );
};

export default GraphViz;
