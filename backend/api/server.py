"""
FastAPI server for Scientific Knowledge Graph Assistant.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

# Import our modules
from ..models.database import Neo4jConnection, get_db
from ..models.graph_schema import PaperNode
from ..data_ingestion import MultiSourceFetcher
from ..kg_construction import GraphBuilder, PaperParser
from ..graph_rag import QueryParser, GraphRetriever, AnswerGenerator
from ..analytics import TrendDetector, ClusterAnalyzer, SummaryGenerator, ExplorationTools

# Initialize FastAPI app
app = FastAPI(
    title="Scientific Knowledge Graph Assistant API",
    description="Graph RAG API for scientific literature exploration",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
db_connection: Optional[Neo4jConnection] = None
graph_builder: Optional[GraphBuilder] = None
query_parser: Optional[QueryParser] = None
graph_retriever: Optional[GraphRetriever] = None
answer_generator: Optional[AnswerGenerator] = None
llm_client = None
trend_detector: Optional[TrendDetector] = None
cluster_analyzer: Optional[ClusterAnalyzer] = None
summary_generator: Optional[SummaryGenerator] = None
exploration_tools: Optional[ExplorationTools] = None


def neo4j_to_json(obj):
    """Convert Neo4j types to JSON-serializable Python types."""
    from neo4j.time import DateTime, Date, Time
    from datetime import datetime, date
    
    if isinstance(obj, (DateTime, Date, Time)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: neo4j_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [neo4j_to_json(item) for item in obj]
    else:
        return obj


# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    max_results: int = 10
    stream: bool = False


class QueryResponse(BaseModel):
    query: str
    answer: str
    context: Dict[str, Any]
    citations: List[str]


class IngestRequest(BaseModel):
    query: str
    max_results_per_source: int = 20
    sources: Optional[List[str]] = None


class IngestResponse(BaseModel):
    status: str
    papers_fetched: int
    papers_added: int
    message: str


class StatsResponse(BaseModel):
    total_nodes: int
    total_relationships: int
    nodes_by_type: Dict[str, int]
    relationships_by_type: Dict[str, int]


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global db_connection, graph_builder, query_parser, graph_retriever, answer_generator, llm_client
    global trend_detector, cluster_analyzer, summary_generator, exploration_tools
    
    print("🚀 Starting Scientific Knowledge Graph Assistant API...")
    
    # Initialize database
    db_connection = get_db()
    
    # Test connection
    if db_connection.test_connection():
        print("✅ Neo4j connection successful")
        db_connection.initialize_database()
    else:
        print("❌ Neo4j connection failed. Please ensure Neo4j is running.")
    
    # Initialize Ollama client
    try:
        import ollama
        llm_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        # Test Ollama
        llm_client.list()
        print("✅ Ollama connection successful")
    except Exception as e:
        print(f"⚠️  Ollama connection failed: {e}")
        print("   LLM features will use heuristic fallbacks")
        llm_client = None
    
    # Initialize components
    graph_builder = GraphBuilder(db_connection)
    query_parser = QueryParser(llm_client)
    graph_retriever = GraphRetriever(db_connection)
    answer_generator = AnswerGenerator(llm_client)
    
    # Initialize analytics components
    trend_detector = TrendDetector(db_connection, llm_client)
    cluster_analyzer = ClusterAnalyzer(db_connection, llm_client)
    summary_generator = SummaryGenerator(db_connection, llm_client)
    exploration_tools = ExplorationTools(db_connection)
    
    print("✅ All services initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global db_connection
    if db_connection:
        db_connection.close()
    print("👋 Shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Scientific Knowledge Graph Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    neo4j_status = db_connection.test_connection() if db_connection else False
    ollama_status = llm_client is not None
    
    return {
        "status": "healthy" if neo4j_status else "degraded",
        "services": {
            "neo4j": "up" if neo4j_status else "down",
            "ollama": "up" if ollama_status else "down"
        }
    }


@app.post("/query", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """Query the knowledge graph with natural language.
    
    Args:
        request: Query request with query string
        
    Returns:
        Answer with context and citations
    """
    if not query_parser or not graph_retriever or not answer_generator:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Parse query
        query_intent = query_parser.parse_query(request.query)
        
        # Retrieve graph context
        graph_context = graph_retriever.retrieve_context(query_intent)
        
        # Generate answer
        answer = answer_generator.generate_answer(
            request.query,
            graph_context,
            stream=False
        )
        
        # Extract citations
        citations = answer_generator.extract_citations(answer)
        
        # Convert Neo4j types to JSON-serializable types
        graph_context = neo4j_to_json(graph_context)
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            context=graph_context,
            citations=citations
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Query processing error: {e}")
        print(f"Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """Stream query response."""
    if not query_parser or not graph_retriever or not answer_generator:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Parse query
        query_intent = query_parser.parse_query(request.query)
        
        # Retrieve graph context
        graph_context = graph_retriever.retrieve_context(query_intent)
        
        # Stream answer
        def generate():
            for chunk in answer_generator.generate_answer(request.query, graph_context, stream=True):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get knowledge graph statistics."""
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        stats = db_connection.get_stats()
        return StatsResponse(
            total_nodes=stats["total_nodes"],
            total_relationships=stats["total_relationships"],
            nodes_by_type=stats["nodes"],
            relationships_by_type=stats["relationships"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_papers(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest papers from multiple sources into the knowledge graph.
    
    Args:
        request: Ingest request with search query
        
    Returns:
        Ingest status
    """
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph builder not initialized")
    
    try:
        # Fetch papers
        fetcher = MultiSourceFetcher()
        results = fetcher.search_all(
            query=request.query,
            max_results_per_source=request.max_results_per_source,
            sources=request.sources
        )
        
        all_papers = fetcher.get_all_papers(results)
        
        # Add papers to graph (in background)
        papers_added = 0
        parser = PaperParser(llm_client)
        
        for paper in all_papers[:50]:  # Limit to 50 for now
            # Extract entities
            methods = parser.extract_methods(paper)
            datasets = parser.extract_datasets(paper)
            
            # Build graph
            stats = graph_builder.build_paper_graph(paper, methods, datasets)
            if stats["papers"] > 0:
                papers_added += 1
        
        return IngestResponse(
            status="success",
            papers_fetched=len(all_papers),
            papers_added=papers_added,
            message=f"Successfully ingested {papers_added} papers from {len(all_papers)} fetched"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/paper/{paper_id}")
async def get_paper(paper_id: str):
    """Get detailed information about a specific paper.
    
    Args:
        paper_id: Paper node ID
        
    Returns:
        Paper details with relationships
    """
    if not graph_retriever:
        raise HTTPException(status_code=503, detail="Graph retriever not initialized")
    
    try:
        paper = graph_retriever.get_paper_details(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get paper: {str(e)}")


class DeleteRequest(BaseModel):
    query: Optional[str] = None
    confirm: bool = False


@app.post("/admin/delete")
async def delete_data(request: DeleteRequest):
    """Delete data from the knowledge graph."""
    if not db_connection:
         raise HTTPException(status_code=503, detail="Database not connected")
    
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")

    try:
        with db_connection.session() as session:
            if request.query:
                # Delete papers matching string and their exclusive relationships
                # Note: This is a safe delete that tries to preserve shared nodes if possible,
                # but for this use case, we usually want to just wipe the matching subgraph.
                cypher = """
                MATCH (p:Paper)
                WHERE toLower(p.title) CONTAINS toLower($text) 
                DETACH DELETE p
                """
                # We also might want to clean up orphan nodes after
                result = session.run(cypher, text=request.query)
                counters = result.consume().counters
                
                # Cleanup orphans (Authors/Methods with no papers)
                session.run("""
                MATCH (n)
                WHERE NOT (n:Paper) AND NOT (n)--()
                DELETE n
                """)
                
                return {
                    "status": "success", 
                    "message": f"Deleted {counters.nodes_deleted} papers matching '{request.query}' and cleaned up orphans."
                }
            else:
                # Delete ALL
                session.run("MATCH (n) DETACH DELETE n")
                return {"status": "success", "message": "All data wiped from database"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/graph/export")
async def export_graph(max_nodes: int = 500):
    """Export graph data for visualization.
    
    Args:
        max_nodes: Maximum number of nodes to return
        
    Returns:
        Graph data in format for visualization
    """
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with db_connection.session() as session:
            # Fetch nodes
            nodes_query = f"""
            MATCH (n)
            RETURN n.node_id AS id,
                   labels(n)[0] AS type,
                   n.title AS title,
                   n.name AS name
            LIMIT {max_nodes}
            """
            nodes_result = session.run(nodes_query)
            nodes = [neo4j_to_json(dict(record)) for record in nodes_result]
            
            # Fetch edges
            edges_query = """
            MATCH (a)-[r]->(b)
            RETURN a.node_id AS source,
                   b.node_id AS target,
                   type(r) AS type
            LIMIT 1000
            """
            edges_result = session.run(edges_query)
            edges = [neo4j_to_json(dict(record)) for record in edges_result]
            
            return {
                "nodes": nodes,
                "edges": edges
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/queries/suggested")
async def get_suggested_queries():
    """Get suggested queries based on the graph content."""
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        with db_connection.session() as session:
            suggestions = []
            
            # 1. Popular Methods
            result = session.run("""
                MATCH (m:Method)<-[:PROPOSES_METHOD]-(p:Paper)
                RETURN m.name, count(p) as count
                ORDER BY count DESC LIMIT 2
            """)
            for record in result:
                if record['m.name']:
                    suggestions.append(f"What papers propose the method '{record['m.name']}'?")

            # 2. Popular Datasets
            result = session.run("""
                MATCH (d:Dataset)<-[:USES_DATASET]-(p:Paper)
                RETURN d.name, count(p) as count
                ORDER BY count DESC LIMIT 1
            """)
            record = result.single()
            if record and record['d.name']:
                suggestions.append(f"Which papers use the {record['d.name']} dataset?")
            
            # 3. Prolific Authors
            result = session.run("""
                MATCH (a:Author)<-[:AUTHORED_BY]-(p:Paper)
                RETURN a.name, count(p) as count
                ORDER BY count DESC LIMIT 1
            """)
            record = result.single()
            if record and record['a.name']:
                suggestions.append(f"What has {record['a.name']} published recently?")
                
            # 4. Recent Papers
            result = session.run("""
                MATCH (p:Paper)
                RETURN p.title
                ORDER BY p.node_id DESC LIMIT 1
            """)
            record = result.single()
            if record and record['p.title']:
                 suggestions.append(f"Summarize the paper '{record['p.title']}'")
            
            # Shuffle and limit
            import random
            random.shuffle(suggestions)
            
            # If we don't have enough suggestions, fill with defaults
            defaults = [
                "Which deep learning methods improved protein folding accuracy after 2020?",
                "Show me all datasets used for drug discovery in the last five years", 
                "Which institutions are leading in quantum computing research?",
                "What are the most cited papers on transformer architectures?"
            ]
            
            if len(suggestions) < 4:
                suggestions.extend(defaults[:4-len(suggestions)])
                
            return suggestions[:4]

    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return [
            "Which deep learning methods improved protein folding accuracy after 2020?",
            "Show me all datasets used for drug discovery in the last five years", 
            "Which institutions are leading in quantum computing research?",
            "What are the most cited papers on transformer architectures?"
        ]


# ============== ADVANCED ANALYTICS ENDPOINTS ==============

@app.get("/analytics/trends/publications")
async def get_publication_trends(time_window_days: int = 365, granularity: str = "month"):
    """Get publication volume trends over time."""
    if not trend_detector:
        raise HTTPException(status_code=503, detail="Trend detector not initialized")
    
    try:
        trends = trend_detector.get_publication_trends(time_window_days, granularity)
        return neo4j_to_json(trends)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@app.get("/analytics/trends/methods")
async def get_method_trends(top_n: int = 10):
    """Get trending methods over time."""
    if not trend_detector:
        raise HTTPException(status_code=503, detail="Trend detector not initialized")
    
    try:
        trends = trend_detector.get_method_trends(top_n)
        return neo4j_to_json(trends)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get method trends: {str(e)}")


@app.get("/analytics/trends/emerging")
async def get_emerging_topics(lookback_months: int = 6):
    """Identify emerging research topics based on growth rate."""
    if not trend_detector:
        raise HTTPException(status_code=503, detail="Trend detector not initialized")
    
    try:
        topics = trend_detector.get_emerging_topics(lookback_months)
        return neo4j_to_json(topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emerging topics: {str(e)}")


@app.get("/analytics/trends/authors")
async def get_author_productivity(top_n: int = 10):
    """Get most productive authors over time."""
    if not trend_detector:
        raise HTTPException(status_code=503, detail="Trend detector not initialized")
    
    try:
        authors = trend_detector.get_author_productivity_trends(top_n)
        return neo4j_to_json(authors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get author trends: {str(e)}")


@app.get("/analytics/clusters/authors")
async def get_author_communities(min_collaborations: int = 2):
    """Find communities of collaborating authors."""
    if not cluster_analyzer:
        raise HTTPException(status_code=503, detail="Cluster analyzer not initialized")
    
    try:
        communities = cluster_analyzer.find_author_communities(min_collaborations)
        return neo4j_to_json(communities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find communities: {str(e)}")


@app.get("/analytics/clusters/methods")
async def get_method_clusters():
    """Find clusters of related methods based on co-occurrence."""
    if not cluster_analyzer:
        raise HTTPException(status_code=503, detail="Cluster analyzer not initialized")
    
    try:
        clusters = cluster_analyzer.find_method_clusters()
        return neo4j_to_json(clusters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find method clusters: {str(e)}")


@app.get("/analytics/clusters/topics")
async def get_topic_clusters():
    """Cluster papers by topic/category."""
    if not cluster_analyzer:
        raise HTTPException(status_code=503, detail="Cluster analyzer not initialized")
    
    try:
        clusters = cluster_analyzer.find_topic_clusters()
        return neo4j_to_json(clusters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find topic clusters: {str(e)}")


@app.get("/analytics/clusters/citations")
async def get_citation_clusters(min_citations: int = 3):
    """Find influential papers through citation analysis."""
    if not cluster_analyzer:
        raise HTTPException(status_code=503, detail="Cluster analyzer not initialized")
    
    try:
        clusters = cluster_analyzer.find_citation_clusters(min_citations)
        return neo4j_to_json(clusters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find citation clusters: {str(e)}")


@app.get("/analytics/landscape")
async def get_research_landscape():
    """Get comprehensive research landscape overview."""
    if not cluster_analyzer:
        raise HTTPException(status_code=503, detail="Cluster analyzer not initialized")
    
    try:
        landscape = cluster_analyzer.get_research_landscape()
        return neo4j_to_json(landscape)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get landscape: {str(e)}")


@app.get("/summary/topic/{topic}")
async def get_topic_summary(topic: str, max_papers: int = 20):
    """Generate a comprehensive summary for a research topic."""
    if not summary_generator:
        raise HTTPException(status_code=503, detail="Summary generator not initialized")
    
    try:
        summary = summary_generator.generate_topic_summary(topic, max_papers)
        return neo4j_to_json(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@app.get("/summary/topic/{topic}/markdown")
async def get_topic_summary_markdown(topic: str, max_papers: int = 20):
    """Generate a Markdown report for a research topic."""
    if not summary_generator:
        raise HTTPException(status_code=503, detail="Summary generator not initialized")
    
    try:
        summary = summary_generator.generate_topic_summary(topic, max_papers)
        markdown = summary_generator.generate_markdown_report(summary)
        return {"markdown": markdown}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate markdown: {str(e)}")


@app.get("/summary/topic/{topic}/executive")
async def get_executive_summary(topic: str):
    """Generate an executive summary using LLM."""
    if not summary_generator:
        raise HTTPException(status_code=503, detail="Summary generator not initialized")
    
    try:
        summary = summary_generator.generate_executive_summary(topic)
        return {"executive_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate executive summary: {str(e)}")


class ComparisonRequest(BaseModel):
    topics: List[str]
    max_papers_per_topic: int = 10


@app.post("/summary/compare")
async def compare_topics(request: ComparisonRequest):
    """Compare multiple research topics."""
    if not summary_generator:
        raise HTTPException(status_code=503, detail="Summary generator not initialized")
    
    try:
        comparison = summary_generator.generate_comparison_report(
            request.topics, 
            request.max_papers_per_topic
        )
        return neo4j_to_json(comparison)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare topics: {str(e)}")


@app.get("/explore/path")
async def find_path(paper_id1: str, paper_id2: str, max_hops: int = 4):
    """Find shortest path between two papers."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        path = exploration_tools.find_path_between_papers(paper_id1, paper_id2, max_hops)
        return neo4j_to_json(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")


@app.get("/explore/common")
async def find_common(paper_id1: str, paper_id2: str):
    """Find common connections between two papers."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        common = exploration_tools.find_common_connections(paper_id1, paper_id2)
        return neo4j_to_json(common)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find common connections: {str(e)}")


@app.get("/explore/neighborhood/{paper_id}")
async def get_neighborhood(paper_id: str, depth: int = 2, limit_per_type: int = 10):
    """Get the neighborhood of a paper."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        neighborhood = exploration_tools.get_paper_neighborhood(paper_id, depth, limit_per_type)
        return neo4j_to_json(neighborhood)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get neighborhood: {str(e)}")


@app.get("/explore/similar/{paper_id}")
async def find_similar(paper_id: str, similarity_type: str = "methods", top_n: int = 10):
    """Find papers similar to a given paper."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        similar = exploration_tools.find_similar_papers(paper_id, similarity_type, top_n)
        return neo4j_to_json(similar)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find similar papers: {str(e)}")


@app.get("/explore/author/{author_name}")
async def get_author_network(author_name: str, depth: int = 2):
    """Get the collaboration network for an author."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        network = exploration_tools.get_author_network(author_name, depth)
        return neo4j_to_json(network)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get author network: {str(e)}")


@app.get("/explore/method/{method_name}")
async def search_by_method(method_name: str, top_n: int = 20):
    """Find all papers using a specific method."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        papers = exploration_tools.search_by_method(method_name, top_n)
        return neo4j_to_json(papers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search by method: {str(e)}")


@app.get("/explore/timeline/{topic}")
async def get_research_timeline(topic: str, years: int = 5):
    """Get a timeline of research activity for a topic."""
    if not exploration_tools:
        raise HTTPException(status_code=503, detail="Exploration tools not initialized")
    
    try:
        timeline = exploration_tools.get_research_timeline(topic, years)
        return neo4j_to_json(timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

