"""
Interactive exploration tools for the knowledge graph.
Provides path finding, similarity search, and graph navigation.
"""

from typing import Dict, Any, List, Optional
from collections import deque


class ExplorationTools:
    """Interactive tools for exploring the knowledge graph."""
    
    def __init__(self, db_connection, embedding_model=None):
        """Initialize exploration tools.
        
        Args:
            db_connection: Neo4j connection
            embedding_model: Optional sentence transformer model
        """
        self.db = db_connection
        self.embedding_model = embedding_model
    
    def find_path_between_papers(
        self,
        paper_id1: str,
        paper_id2: str,
        max_hops: int = 4
    ) -> Dict[str, Any]:
        """Find shortest path between two papers.
        
        Args:
            paper_id1: First paper ID
            paper_id2: Second paper ID
            max_hops: Maximum path length
            
        Returns:
            Path information
        """
        query = f"""
        MATCH path = shortestPath(
            (p1:Paper {{node_id: $id1}})-[*1..{max_hops}]-(p2:Paper {{node_id: $id2}})
        )
        RETURN path,
               length(path) AS path_length,
               [node IN nodes(path) | labels(node)[0]] AS node_types,
               [node IN nodes(path) | coalesce(node.title, node.name, node.node_id)] AS node_names,
               [rel IN relationships(path) | type(rel)] AS relationship_types
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, id1=paper_id1, id2=paper_id2)
                record = result.single()
                
                if record:
                    return {
                        "found": True,
                        "path_length": record['path_length'],
                        "nodes": [
                            {"type": t, "name": n}
                            for t, n in zip(record['node_types'], record['node_names'])
                        ],
                        "relationships": record['relationship_types']
                    }
                else:
                    return {
                        "found": False,
                        "message": f"No path found within {max_hops} hops"
                    }
        except Exception as e:
            return {"error": str(e)}
    
    def find_common_connections(
        self,
        paper_id1: str,
        paper_id2: str
    ) -> Dict[str, Any]:
        """Find common connections between two papers.
        
        Args:
            paper_id1: First paper ID
            paper_id2: Second paper ID
            
        Returns:
            Common connections
        """
        query = """
        MATCH (p1:Paper {node_id: $id1})-[r1]->(common)<-[r2]-(p2:Paper {node_id: $id2})
        RETURN labels(common)[0] AS connection_type,
               coalesce(common.name, common.title, common.node_id) AS connection_name,
               type(r1) AS rel1,
               type(r2) AS rel2
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, id1=paper_id1, id2=paper_id2)
                
                connections = []
                for record in result:
                    connections.append({
                        "type": record['connection_type'],
                        "name": record['connection_name'],
                        "relationship1": record['rel1'],
                        "relationship2": record['rel2']
                    })
                
                return {
                    "paper1": paper_id1,
                    "paper2": paper_id2,
                    "common_connections": connections,
                    "count": len(connections)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_paper_neighborhood(
        self,
        paper_id: str,
        depth: int = 2,
        limit_per_type: int = 10
    ) -> Dict[str, Any]:
        """Get the neighborhood of a paper up to a certain depth.
        
        Args:
            paper_id: Paper ID to explore
            depth: How many hops to explore
            limit_per_type: Max nodes per type
            
        Returns:
            Neighborhood data
        """
        query = f"""
        MATCH (p:Paper {{node_id: $paper_id}})-[r*1..{depth}]-(connected)
        WITH DISTINCT connected, labels(connected)[0] AS node_type
        WITH node_type, collect({{
            id: connected.node_id,
            name: coalesce(connected.title, connected.name, connected.node_id),
            type: node_type
        }})[0..{limit_per_type}] AS nodes
        RETURN node_type, nodes
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, paper_id=paper_id)
                
                neighborhood = {}
                for record in result:
                    neighborhood[record['node_type']] = record['nodes']
                
                return {
                    "center_paper": paper_id,
                    "depth": depth,
                    "neighborhood": neighborhood
                }
        except Exception as e:
            return {"error": str(e)}
    
    def find_similar_papers(
        self,
        paper_id: str,
        similarity_type: str = "methods",
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Find papers similar to a given paper.
        
        Args:
            paper_id: Reference paper ID
            similarity_type: 'methods', 'authors', 'citations', or 'topics'
            top_n: Number of similar papers
            
        Returns:
            Similar papers
        """
        if similarity_type == "methods":
            query = """
            MATCH (p1:Paper {node_id: $paper_id})-[:PROPOSES_METHOD|USES_METHOD]->(m:Method)<-[:PROPOSES_METHOD|USES_METHOD]-(p2:Paper)
            WHERE p1 <> p2
            WITH p2, count(m) AS shared_methods
            RETURN p2.node_id AS paper_id,
                   p2.title AS title,
                   shared_methods AS similarity_score
            ORDER BY shared_methods DESC
            LIMIT $top_n
            """
        elif similarity_type == "authors":
            query = """
            MATCH (p1:Paper {node_id: $paper_id})-[:AUTHORED_BY]->(a:Author)<-[:AUTHORED_BY]-(p2:Paper)
            WHERE p1 <> p2
            WITH p2, count(a) AS shared_authors
            RETURN p2.node_id AS paper_id,
                   p2.title AS title,
                   shared_authors AS similarity_score
            ORDER BY shared_authors DESC
            LIMIT $top_n
            """
        elif similarity_type == "citations":
            query = """
            MATCH (p1:Paper {node_id: $paper_id})-[:CITES]->(cited:Paper)<-[:CITES]-(p2:Paper)
            WHERE p1 <> p2
            WITH p2, count(cited) AS shared_citations
            RETURN p2.node_id AS paper_id,
                   p2.title AS title,
                   shared_citations AS similarity_score
            ORDER BY shared_citations DESC
            LIMIT $top_n
            """
        else:  # topics/categories
            query = """
            MATCH (p1:Paper {node_id: $paper_id})
            WITH p1, p1.categories AS cats1
            MATCH (p2:Paper)
            WHERE p1 <> p2 AND p2.categories IS NOT NULL
            WITH p2, p1, cats1,
                 [cat IN p2.categories WHERE cat IN cats1] AS shared_cats
            WHERE size(shared_cats) > 0
            RETURN p2.node_id AS paper_id,
                   p2.title AS title,
                   size(shared_cats) AS similarity_score
            ORDER BY similarity_score DESC
            LIMIT $top_n
            """
        
        try:
            with self.db.session() as session:
                result = session.run(query, paper_id=paper_id, top_n=top_n)
                
                similar = []
                for record in result:
                    similar.append({
                        "paper_id": record['paper_id'],
                        "title": record['title'],
                        "similarity_score": record['similarity_score']
                    })
                
                return {
                    "reference_paper": paper_id,
                    "similarity_type": similarity_type,
                    "similar_papers": similar
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_author_network(self, author_name: str, depth: int = 2) -> Dict[str, Any]:
        """Get the collaboration network for an author.
        
        Args:
            author_name: Author name to explore
            depth: Number of collaboration hops
            
        Returns:
            Author network data
        """
        query = f"""
        MATCH (a:Author)
        WHERE toLower(a.name) CONTAINS toLower($author_name)
        WITH a
        MATCH path = (a)-[:AUTHORED_BY|COLLABORATED_WITH*1..{depth}]-(connected:Author)
        WHERE a <> connected
        WITH DISTINCT connected, length(path) AS distance
        RETURN connected.name AS collaborator,
               connected.node_id AS collaborator_id,
               distance
        ORDER BY distance, collaborator
        LIMIT 50
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, author_name=author_name)
                
                network = []
                for record in result:
                    network.append({
                        "collaborator": record['collaborator'],
                        "collaborator_id": record['collaborator_id'],
                        "distance": record['distance']
                    })
                
                return {
                    "author": author_name,
                    "depth": depth,
                    "network": network,
                    "total_collaborators": len(network)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def search_by_method(self, method_name: str, top_n: int = 20) -> Dict[str, Any]:
        """Find all papers using a specific method.
        
        Args:
            method_name: Method to search for
            top_n: Maximum papers to return
            
        Returns:
            Papers using the method
        """
        query = """
        MATCH (p:Paper)-[:PROPOSES_METHOD|USES_METHOD]->(m:Method)
        WHERE toLower(m.name) CONTAINS toLower($method_name)
        OPTIONAL MATCH (p)-[:AUTHORED_BY]->(a:Author)
        WITH p, m, collect(a.name) AS authors
        RETURN p.node_id AS paper_id,
               p.title AS title,
               p.publication_date AS date,
               m.name AS method,
               authors
        ORDER BY p.publication_date DESC
        LIMIT $top_n
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, method_name=method_name, top_n=top_n)
                
                papers = []
                for record in result:
                    papers.append({
                        "paper_id": record['paper_id'],
                        "title": record['title'],
                        "date": record['date'],
                        "method": record['method'],
                        "authors": record['authors'][:5]
                    })
                
                return {
                    "method_search": method_name,
                    "papers": papers,
                    "total_found": len(papers)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_research_timeline(self, topic: str, years: int = 5) -> Dict[str, Any]:
        """Get a timeline of research activity for a topic.
        
        Args:
            topic: Research topic
            years: Number of years to look back
            
        Returns:
            Timeline data
        """
        query = """
        MATCH (p:Paper)
        WHERE (toLower(p.title) CONTAINS toLower($topic)
               OR toLower(p.abstract) CONTAINS toLower($topic))
              AND p.publication_date IS NOT NULL
        WITH p, date(p.publication_date) AS pubDate
        WHERE pubDate >= date() - duration({years: $years})
        WITH pubDate.year AS year, pubDate.month AS month, count(p) AS papers
        RETURN year, month, papers
        ORDER BY year, month
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, topic=topic, years=years)
                
                timeline = []
                for record in result:
                    timeline.append({
                        "year": record['year'],
                        "month": record['month'],
                        "paper_count": record['papers']
                    })
                
                return {
                    "topic": topic,
                    "years": years,
                    "timeline": timeline
                }
        except Exception as e:
            return {"error": str(e)}
