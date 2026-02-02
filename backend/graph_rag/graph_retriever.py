"""
Graph retrieval for finding relevant context from the knowledge graph.
"""

from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
from ..models.database import Neo4jConnection
from ..models.graph_schema import QueryIntent


class GraphRetriever:
    """Retrieve relevant graph context for queries."""
    
    def __init__(self, db: Neo4jConnection, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize graph retriever.
        
        Args:
            db: Neo4j database connection
            embedding_model: Model for embeddings
        """
        self.db = db
        self.embedder = SentenceTransformer(embedding_model)
    
    def semantic_search(
        self,
        query_text: str,
        top_k: int = 10,
        node_type: str = "Paper"
    ) -> List[Dict[str, Any]]:
        """Find nodes using semantic similarity.
        
        Args:
            query_text: Search query
            top_k: Number of results to return
            node_type: Type of nodes to search (default: Paper)
            
        Returns:
            List of node dictionaries with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedder.encode(query_text, convert_to_numpy=True).tolist()
        
        with self.db.session() as session:
            # Fetch all nodes with embeddings
            cypher_query = f"""
            MATCH (n:{node_type})
            WHERE n.embedding IS NOT NULL
            RETURN n.node_id AS node_id,
                   n.title AS title,
                   n.abstract AS abstract,
                   n.embedding AS embedding
            LIMIT 1000
            """
            
            results = session.run(cypher_query)
            
            # Calculate similarities
            scored_results = []
            for record in results:
                node_embedding = record["embedding"]
                if node_embedding:
                    # Cosine similarity
                    similarity = self._cosine_similarity(query_embedding, node_embedding)
                    scored_results.append({
                        "node_id": record["node_id"],
                        "title": record["title"],
                        "abstract": record["abstract"],
                        "similarity": similarity
                    })
            
            # Sort by similarity and return top_k
            scored_results.sort(key=lambda x: x["similarity"], reverse=True)
            return scored_results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def multi_hop_traversal(
        self,
        start_nodes: List[str],
        max_hops: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform multi-hop graph traversal.
        
        Args:
            start_nodes: List of starting node IDs
            max_hops: Maximum traversal depth
            relationship_types: Optional filter for relationship types
            
        Returns:
            Dictionary with nodes and edges found
        """
        if not start_nodes:
            return {"nodes": [], "edges": []}
        
        with self.db.session() as session:
            # Build relationship filter
            rel_filter = ""
            if relationship_types:
                rel_types = "|".join(relationship_types)
                rel_filter = f":{rel_types}"
            
            # Cypher query for multi-hop traversal
            cypher_query = f"""
            MATCH path = (start)-[{rel_filter}*1..{max_hops}]-(connected)
            WHERE start.node_id IN $start_nodes
            WITH path, relationships(path) AS rels, nodes(path) AS node_list
            UNWIND node_list AS n
            WITH DISTINCT n, path, rels
            RETURN 
                n.node_id AS node_id,
                labels(n)[0] AS node_type,
                properties(n) AS properties,
                rels,
                path
            LIMIT 500
            """
            
            result = session.run(cypher_query, {"start_nodes": start_nodes})
            
            nodes = {}
            edges = []
            
            for record in result:
                node_id = record["node_id"]
                if node_id not in nodes:
                    nodes[node_id] = {
                        "id": node_id,
                        "type": record["node_type"],
                        "properties": dict(record["properties"])
                    }
                
                # Extract edges from path
                for rel in record["rels"]:
                    edge = {
                        "source": rel.start_node["node_id"],
                        "target": rel.end_node["node_id"],
                        "type": rel.type
                    }
                    if edge not in edges:
                        edges.append(edge)
            
            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }
    
    def get_all_papers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all papers from the database.
        
        Args:
            limit: Maximum number of papers to return
            
        Returns:
            List of paper dictionaries
        """
        with self.db.session() as session:
            cypher_query = f"""
            MATCH (p:Paper)
            RETURN p.node_id AS node_id,
                   p.title AS title,
                   p.abstract AS abstract
            ORDER BY p.publication_date DESC
            LIMIT {limit}
            """
            
            results = session.run(cypher_query)
            papers = []
            for record in results:
                papers.append({
                    "node_id": record["node_id"],
                    "title": record["title"],
                    "abstract": record["abstract"],
                    "similarity": 1.0  # Perfect match for listing
                })
            return papers
    
    def _is_list_all_query(self, query: str) -> bool:
        """Check if the query is asking to list all papers.
        
        Args:
            query: Original query string
            
        Returns:
            True if the query is a "list all" type query
        """
        import re
        query_lower = query.lower()
        
        # Simple patterns for exact matches
        simple_patterns = [
            "list the papers", 
            "list papers",
            "show papers",
            "get papers",
            "what papers are there",
            "how many papers",
            "count papers"
        ]
        
        # Regex patterns for flexible matching
        regex_patterns = [
            r"list\s+(?:all\s+)?(?:\d+\s+)?papers",  # list all papers, list all 20 papers, list 20 papers
            r"show\s+(?:all\s+)?(?:\d+\s+)?papers",  # show all papers, show all 20 papers
            r"get\s+(?:all\s+)?(?:\d+\s+)?papers",   # get all papers
            r"all\s+(?:\d+\s+)?papers",              # all papers, all 20 papers
        ]
        
        # Check simple patterns first
        if any(pattern in query_lower for pattern in simple_patterns):
            return True
        
        # Check regex patterns
        for pattern in regex_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False

    def retrieve_context(
        self,
        query_intent: QueryIntent
    ) -> Dict[str, Any]:
        """Retrieve full context for a query.
        
        Args:
            query_intent: Parsed query intent
            
        Returns:
            Dictionary with relevant nodes and edges
        """
        # Check if this is a "list all papers" query
        if self._is_list_all_query(query_intent.original_query):
            # Return all papers for listing queries
            search_results = self.get_all_papers(limit=100)
            return {
                "nodes": [],
                "edges": [],
                "search_results": search_results,
                "query_intent": query_intent.dict()
            }
        
        # Step 1: Semantic search to find starting nodes
        search_results = self.semantic_search(
            query_text=query_intent.original_query,
            top_k=10  # Increased from 5 to 10 for better coverage
        )
        
        start_nodes = [r["node_id"] for r in search_results]
        
        # Step 2: Multi-hop traversal to find connected nodes
        graph_context = self.multi_hop_traversal(
            start_nodes=start_nodes,
            max_hops=query_intent.max_hops
        )
        
        # Step 3: Add semantic search results to context
        graph_context["search_results"] = search_results
        graph_context["query_intent"] = query_intent.dict()
        
        return graph_context
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full details of a paper including relationships.
        
        Args:
            paper_id: Paper node ID
            
        Returns:
            Dictionary with paper details and relationships
        """
        with self.db.session() as session:
            cypher_query = """
            MATCH (p:Paper {node_id: $paper_id})
            OPTIONAL MATCH (p)-[:AUTHORED_BY]->(a:Author)
            OPTIONAL MATCH (p)-[:PROPOSES_METHOD]->(m:Method)
            OPTIONAL MATCH (p)-[:USES_DATASET]->(d:Dataset)
            OPTIONAL MATCH (p)-[:CITES]->(cited:Paper)
            RETURN 
                p,
                collect(DISTINCT a.name) AS authors,
                collect(DISTINCT m.name) AS methods,
                collect(DISTINCT d.name) AS datasets,
                collect(DISTINCT cited.title) AS citations
            """
            
            result = session.run(cypher_query, {"paper_id": paper_id})
            record = result.single()
            
            if not record:
                return None
            
            paper = dict(record["p"])
            paper["authors"] = record["authors"]
            paper["methods"] = record["methods"]
            paper["datasets"] = record["datasets"]
            paper["citations"] = record["citations"]
            
            return paper
