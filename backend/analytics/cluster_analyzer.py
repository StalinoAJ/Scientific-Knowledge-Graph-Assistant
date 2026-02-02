"""
Cluster analysis for research communities and topic groupings.
Uses graph algorithms to identify research clusters and communities.
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
import json


class ClusterAnalyzer:
    """Analyze research clusters and communities in the knowledge graph."""
    
    def __init__(self, db_connection, llm_client=None):
        """Initialize cluster analyzer.
        
        Args:
            db_connection: Neo4j connection
            llm_client: Optional Ollama client for cluster descriptions
        """
        self.db = db_connection
        self.llm_client = llm_client
    
    def find_author_communities(self, min_collaborations: int = 2) -> Dict[str, Any]:
        """Find communities of collaborating authors.
        
        Args:
            min_collaborations: Minimum collaborations to form connection
            
        Returns:
            Author communities data
        """
        # Find co-authorship relationships
        query = """
        MATCH (a1:Author)<-[:AUTHORED_BY]-(p:Paper)-[:AUTHORED_BY]->(a2:Author)
        WHERE a1.node_id < a2.node_id
        WITH a1, a2, count(p) AS collaborations
        WHERE collaborations >= $min_collab
        RETURN a1.name AS author1, a1.node_id AS id1,
               a2.name AS author2, a2.node_id AS id2,
               collaborations
        ORDER BY collaborations DESC
        LIMIT 100
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, min_collab=min_collaborations)
                
                # Build adjacency list
                adjacency = defaultdict(set)
                author_names = {}
                collaboration_weights = {}
                
                for record in result:
                    id1, id2 = record['id1'], record['id2']
                    adjacency[id1].add(id2)
                    adjacency[id2].add(id1)
                    author_names[id1] = record['author1']
                    author_names[id2] = record['author2']
                    collaboration_weights[(id1, id2)] = record['collaborations']
                
                # Simple community detection using connected components
                communities = self._find_connected_components(adjacency)
                
                # Format output
                formatted_communities = []
                for i, community in enumerate(communities):
                    if len(community) >= 2:
                        members = [
                            {"id": aid, "name": author_names.get(aid, "Unknown")}
                            for aid in community
                        ]
                        formatted_communities.append({
                            "community_id": i + 1,
                            "size": len(community),
                            "members": members
                        })
                
                return {
                    "total_communities": len(formatted_communities),
                    "communities": sorted(formatted_communities, key=lambda x: -x['size'])
                }
        except Exception as e:
            return {"error": str(e), "communities": []}
    
    def _find_connected_components(self, adjacency: Dict[str, set]) -> List[set]:
        """Find connected components using BFS.
        
        Args:
            adjacency: Adjacency list
            
        Returns:
            List of connected components
        """
        visited = set()
        components = []
        
        for node in adjacency:
            if node not in visited:
                component = set()
                queue = [node]
                
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        queue.extend(adjacency[current] - visited)
                
                components.append(component)
        
        return components
    
    def find_method_clusters(self) -> Dict[str, Any]:
        """Find clusters of related methods based on co-occurrence in papers.
        
        Returns:
            Method clusters data
        """
        query = """
        MATCH (m1:Method)<-[:PROPOSES_METHOD|USES_METHOD]-(p:Paper)-[:PROPOSES_METHOD|USES_METHOD]->(m2:Method)
        WHERE m1.node_id < m2.node_id
        WITH m1.name AS method1, m2.name AS method2, count(p) AS co_occurrences
        WHERE co_occurrences >= 2
        RETURN method1, method2, co_occurrences
        ORDER BY co_occurrences DESC
        LIMIT 50
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query)
                
                method_pairs = []
                for record in result:
                    method_pairs.append({
                        "method1": record['method1'],
                        "method2": record['method2'],
                        "co_occurrences": record['co_occurrences']
                    })
                
                return {
                    "method_relationships": method_pairs,
                    "total_pairs": len(method_pairs)
                }
        except Exception as e:
            return {"error": str(e), "method_relationships": []}
    
    def find_topic_clusters(self) -> Dict[str, Any]:
        """Cluster papers by topic/category similarity.
        
        Returns:
            Topic clusters data
        """
        query = """
        MATCH (p:Paper)
        WHERE p.categories IS NOT NULL AND size(p.categories) > 0
        WITH p.categories AS categories, count(p) AS paper_count
        UNWIND categories AS category
        WITH category, sum(paper_count) AS total_papers
        RETURN category, total_papers
        ORDER BY total_papers DESC
        LIMIT 20
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query)
                
                topics = []
                for record in result:
                    topics.append({
                        "category": record['category'],
                        "paper_count": record['total_papers']
                    })
                
                return {
                    "top_topics": topics,
                    "total_categories": len(topics)
                }
        except Exception as e:
            return {"error": str(e), "top_topics": []}
    
    def find_citation_clusters(self, min_citations: int = 3) -> Dict[str, Any]:
        """Find clusters of highly interconnected papers through citations.
        
        Args:
            min_citations: Minimum citations to consider
            
        Returns:
            Citation cluster data
        """
        query = """
        MATCH (p1:Paper)-[:CITES]->(p2:Paper)
        WITH p2, count(p1) AS citation_count
        WHERE citation_count >= $min_cites
        RETURN p2.node_id AS paper_id,
               p2.title AS title,
               citation_count
        ORDER BY citation_count DESC
        LIMIT 20
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, min_cites=min_citations)
                
                influential_papers = []
                for record in result:
                    influential_papers.append({
                        "paper_id": record['paper_id'],
                        "title": record['title'],
                        "citation_count": record['citation_count']
                    })
                
                return {
                    "influential_papers": influential_papers,
                    "min_citations_threshold": min_citations
                }
        except Exception as e:
            return {"error": str(e), "influential_papers": []}
    
    def get_research_landscape(self) -> Dict[str, Any]:
        """Get overall research landscape overview.
        
        Returns:
            Comprehensive landscape data
        """
        try:
            author_communities = self.find_author_communities()
            method_clusters = self.find_method_clusters()
            topic_clusters = self.find_topic_clusters()
            citation_clusters = self.find_citation_clusters()
            
            return {
                "author_communities": author_communities,
                "method_relationships": method_clusters,
                "topic_distribution": topic_clusters,
                "influential_papers": citation_clusters
            }
        except Exception as e:
            return {"error": str(e)}
    
    def describe_cluster_with_llm(self, cluster_data: Dict[str, Any]) -> str:
        """Use LLM to generate natural language cluster description.
        
        Args:
            cluster_data: Cluster data to describe
            
        Returns:
            Natural language description
        """
        if not self.llm_client:
            return "LLM not available for cluster description."
        
        prompt = f"""Analyze the following research cluster data and provide insights:

Cluster Data:
{json.dumps(cluster_data, indent=2)}

Please provide:
1. Description of the main research communities
2. Key relationships between methods/topics
3. Notable patterns in the research landscape
4. Potential collaboration opportunities

Keep the analysis focused and actionable."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating description: {e}"
