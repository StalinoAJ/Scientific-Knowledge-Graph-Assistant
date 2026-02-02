"""
Knowledge graph construction and population with Neo4j.
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from ..models.graph_schema import (
    PaperNode, AuthorNode, InstitutionNode,
    MethodNode, DatasetNode, GraphEdge, EdgeType
)
from ..models.database import Neo4jConnection


class GraphBuilder:
    """Build and populate the knowledge graph in Neo4j."""
    
    def __init__(self, db: Neo4jConnection, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize graph builder.
        
        Args:
            db: Neo4j database connection
            embedding_model: Sentence transformer model for embeddings
        """
        self.db = db
        self.embedder = SentenceTransformer(embedding_model)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.embedder.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def add_paper(self, paper: PaperNode) -> bool:
        """Add a paper node to the graph.
        
        Args:
            paper: Paper to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding for semantic search
            text_for_embedding = f"{paper.title} {paper.abstract}"
            embedding = self.generate_embedding(text_for_embedding)
            
            with self.db.session() as session:
                query = """
                MERGE (p:Paper {node_id: $node_id})
                SET p.title = $title,
                    p.abstract = $abstract,
                    p.authors = $authors,
                    p.publication_date = datetime($publication_date),
                    p.venue = $venue,
                    p.url = $url,
                    p.pdf_url = $pdf_url,
                    p.categories = $categories,
                    p.citations_count = $citations_count,
                    p.source = $source,
                    p.embedding = $embedding
                RETURN p
                """
                
                params = {
                    "node_id": paper.node_id,
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "authors": paper.authors,
                    "publication_date": paper.publication_date.isoformat() if paper.publication_date else None,
                    "venue": paper.venue,
                    "url": paper.url,
                    "pdf_url": paper.pdf_url,
                    "categories": paper.categories,
                    "citations_count": paper.citations_count,
                    "source": paper.source,
                    "embedding": embedding
                }
                
                session.run(query, params)
                return True
                
        except Exception as e:
            print(f"Error adding paper {paper.node_id}: {e}")
            return False
    
    def add_author(self, author: AuthorNode) -> bool:
        """Add an author node to the graph.
        
        Args:
            author: Author to add
            
        Returns:
            True if successful
        """
        try:
            with self.db.session() as session:
                query = """
                MERGE (a:Author {node_id: $node_id})
                SET a.name = $name,
                    a.email = $email,
                    a.h_index = $h_index,
                    a.total_citations = $total_citations,
                    a.affiliations = $affiliations
                RETURN a
                """
                
                params = {
                    "node_id": author.node_id,
                    "name": author.name,
                    "email": author.email,
                    "h_index": author.h_index,
                    "total_citations": author.total_citations,
                    "affiliations": author.affiliations
                }
                
                session.run(query, params)
                return True
                
        except Exception as e:
            print(f"Error adding author {author.node_id}: {e}")
            return False
    
    def add_institution(self, institution: InstitutionNode) -> bool:
        """Add an institution node."""
        try:
            with self.db.session() as session:
                query = """
                MERGE (i:Institution {node_id: $node_id})
                SET i.name = $name,
                    i.country = $country,
                    i.department = $department
                RETURN i
                """
                
                params = {
                    "node_id": institution.node_id,
                    "name": institution.name,
                    "country": institution.country,
                    "department": institution.department
                }
                
                session.run(query, params)
                return True
                
        except Exception as e:
            print(f"Error adding institution {institution.node_id}: {e}")
            return False
    
    def add_method(self, method: MethodNode) -> bool:
        """Add a method node."""
        try:
            with self.db.session() as session:
                query = """
                MERGE (m:Method {node_id: $node_id})
                SET m.name = $name,
                    m.description = $description,
                    m.category = $category
                RETURN m
                """
                
                params = {
                    "node_id": method.node_id,
                    "name": method.name,
                    "description": method.description,
                    "category": method.category
                }
                
                session.run(query, params)
                return True
                
        except Exception as e:
            print(f"Error adding method {method.node_id}: {e}")
            return False
    
    def add_dataset(self, dataset: DatasetNode) -> bool:
        """Add a dataset node."""
        try:
            with self.db.session() as session:
                query = """
                MERGE (d:Dataset {node_id: $node_id})
                SET d.name = $name,
                    d.description = $description,
                    d.size = $size,
                    d.url = $url,
                    d.domain = $domain
                RETURN d
                """
                
                params = {
                    "node_id": dataset.node_id,
                    "name": dataset.name,
                    "description": dataset.description,
                    "size": dataset.size,
                    "url": dataset.url,
                    "domain": dataset.domain
                }
                
                session.run(query, params)
                return True
                
        except Exception as e:
            print(f"Error adding dataset {dataset.node_id}: {e}")
            return False
    
    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge between two nodes.
        
        Args:
            edge: Edge to add
            
        Returns:
            True if successful
        """
        try:
            with self.db.session() as session:
                # Convert properties dict to JSON if not empty, otherwise skip
                import json
                props_json = json.dumps(edge.properties) if edge.properties else "{}"
                
                # Dynamic edge type creation
                query = f"""
                MATCH (src {{node_id: $source_id}})
                MATCH (tgt {{node_id: $target_id}})
                MERGE (src)-[r:{edge.edge_type.value}]->(tgt)
                SET r.weight = $weight,
                    r.properties_json = $properties_json
                RETURN r
                """
                
                params = {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "weight": edge.weight,
                    "properties_json": props_json
                }
                
                result = session.run(query, params)
                record = result.single()
                
                if record:
                    return True
                else:
                    print(f"⚠️  No edge created: {edge.source_id} -> {edge.target_id}. Nodes might not exist.")
                    return False
                
        except Exception as e:
            print(f"❌ Error adding edge {edge.source_id} -> {edge.target_id}: {e}")
            return False
    
    def connect_paper_to_authors(self, paper_id: str, author_names: List[str]) -> int:
        """Create AUTHORED_BY relationships between paper and authors.
        
        Args:
            paper_id: Paper node ID
            author_names: List of author names
            
        Returns:
            Number of relationships created
        """
        count = 0
        for author_name in author_names:
            # Create author node if doesn't exist
            author_id = f"author:{author_name.lower().replace(' ', '_')}"
            author = AuthorNode(
                node_id=author_id,
                name=author_name
            )
            self.add_author(author)
            
            # Create edge
            edge = GraphEdge(
                source_id=paper_id,
                target_id=author_id,
                edge_type=EdgeType.AUTHORED_BY
            )
            if self.add_edge(edge):
                count += 1
        
        return count
    
    def connect_paper_to_methods(self, paper_id: str, methods: List[MethodNode]) -> int:
        """Create PROPOSES_METHOD relationships.
        
        Args:
            paper_id: Paper node ID
            methods: List of method nodes
            
        Returns:
            Number of relationships created
        """
        count = 0
        for method in methods:
            self.add_method(method)
            edge = GraphEdge(
                source_id=paper_id,
                target_id=method.node_id,
                edge_type=EdgeType.PROPOSES_METHOD
            )
            if self.add_edge(edge):
                count += 1
        return count
    
    def connect_paper_to_datasets(self, paper_id: str, datasets: List[DatasetNode]) -> int:
        """Create USES_DATASET relationships.
        
        Args:
            paper_id: Paper node ID
            datasets: List of dataset nodes
            
        Returns:
            Number of relationships created
        """
        count = 0
        for dataset in datasets:
            self.add_dataset(dataset)
            edge = GraphEdge(
                source_id=paper_id,
                target_id=dataset.node_id,
                edge_type=EdgeType.USES_DATASET
            )
            if self.add_edge(edge):
                count += 1
        return count
    
    def create_citation_edge(self, citing_paper_id: str, cited_paper_id: str) -> bool:
        """Create CITES relationship between papers.
        
        Args:
            citing_paper_id: ID of paper that cites
            cited_paper_id: ID of paper being cited
            
        Returns:
            True if successful
        """
        edge = GraphEdge(
            source_id=citing_paper_id,
            target_id=cited_paper_id,
            edge_type=EdgeType.CITES
        )
        return self.add_edge(edge)
    
    def build_paper_graph(
        self,
        paper: PaperNode,
        methods: Optional[List[MethodNode]] = None,
        datasets: Optional[List[DatasetNode]] = None
    ) -> Dict[str, int]:
        """Comprehensive graph building for a single paper.
        
        Args:
            paper: Paper to add
            methods: Extracted methods
            datasets: Extracted datasets
            
        Returns:
            Dictionary with counts of created nodes/edges
        """
        stats = {
            "papers": 0,
            "authors": 0,
            "methods": 0,
            "datasets": 0,
            "edges": 0
        }
        
        # Add paper
        if self.add_paper(paper):
            stats["papers"] = 1
            print(f"✓ Added paper: {paper.node_id}")
        
        # Add authors and connections
        author_edges = self.connect_paper_to_authors(paper.node_id, paper.authors)
        stats["edges"] += author_edges
        stats["authors"] = len(paper.authors)
        print(f"  → Created {author_edges} AUTHORED_BY edges for {len(paper.authors)} authors")
        
        # Add methods and connections
        if methods:
            method_edges = self.connect_paper_to_methods(paper.node_id, methods)
            stats["edges"] += method_edges
            stats["methods"] = len(methods)
            print(f"  → Created {method_edges} PROPOSES_METHOD edges for {len(methods)} methods")
        
        # Add datasets and connections
        if datasets:
            dataset_edges = self.connect_paper_to_datasets(paper.node_id, datasets)
            stats["edges"] += dataset_edges
            stats["datasets"] = len(datasets)
            print(f"  → Created {dataset_edges} USES_DATASET edges for {len(datasets)} datasets")
        
        print(f"  Total edges created: {stats['edges']}\n")
        return stats
