"""
Graph schema definitions for the Scientific Knowledge Graph.

Node Types:
- Paper: Scientific publications
- Author: Paper authors
- Institution: Research institutions/universities
- Method: Research methods, algorithms, techniques
- Dataset: Research datasets
- Result: Key findings/results

Edge Types:
- CITES: Paper cites another paper
- AUTHORED_BY: Paper written by author
- AFFILIATED_WITH: Author affiliated with institution
- USES_DATASET: Paper uses a dataset
- PROPOSES_METHOD: Paper proposes a method
- EXTENDS_METHOD: Method extends another method
- COLLABORATES_WITH: Author collaborates with another author
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""
    PAPER = "Paper"
    AUTHOR = "Author"
    INSTITUTION = "Institution"
    METHOD = "Method"
    DATASET = "Dataset"
    RESULT = "Result"


class EdgeType(str, Enum):
    """Types of edges in the knowledge graph."""
    CITES = "CITES"
    AUTHORED_BY = "AUTHORED_BY"
    AFFILIATED_WITH = "AFFILIATED_WITH"
    USES_DATASET = "USES_DATASET"
    PROPOSES_METHOD = "PROPOSES_METHOD"
    EXTENDS_METHOD = "EXTENDS_METHOD"
    COLLABORATES_WITH = "COLLABORATES_WITH"


class PaperNode(BaseModel):
    """Paper node in the knowledge graph."""
    node_id: str = Field(..., description="Unique identifier (e.g., arXiv ID, DOI)")
    title: str
    abstract: str
    authors: List[str]
    publication_date: Optional[datetime] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    categories: List[str] = []
    citations_count: int = 0
    embedding: Optional[List[float]] = None
    source: str = Field(..., description="Source: arxiv, pubmed, semantic_scholar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "arxiv:2301.12345",
                "title": "Deep Learning for Protein Folding",
                "abstract": "We present a novel approach...",
                "authors": ["John Doe", "Jane Smith"],
                "publication_date": "2023-01-15",
                "venue": "Nature",
                "categories": ["cs.LG", "q-bio.BM"],
                "source": "arxiv"
            }
        }


class AuthorNode(BaseModel):
    """Author node in the knowledge graph."""
    node_id: str = Field(..., description="Unique identifier for author")
    name: str
    email: Optional[str] = None
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    affiliations: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "author:john_doe",
                "name": "John Doe",
                "affiliations": ["MIT", "Stanford University"]
            }
        }


class InstitutionNode(BaseModel):
    """Institution node in the knowledge graph."""
    node_id: str
    name: str
    country: Optional[str] = None
    department: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "institution:mit",
                "name": "Massachusetts Institute of Technology",
                "country": "USA"
            }
        }


class MethodNode(BaseModel):
    """Method/technique node in the knowledge graph."""
    node_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None  # e.g., "deep_learning", "optimization"
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "method:alphafold2",
                "name": "AlphaFold 2",
                "description": "Deep learning method for protein structure prediction",
                "category": "deep_learning"
            }
        }


class DatasetNode(BaseModel):
    """Dataset node in the knowledge graph."""
    node_id: str
    name: str
    description: Optional[str] = None
    size: Optional[str] = None
    url: Optional[str] = None
    domain: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "dataset:imagenet",
                "name": "ImageNet",
                "description": "Large visual database for object recognition",
                "domain": "computer_vision"
            }
        }


class ResultNode(BaseModel):
    """Result/finding node in the knowledge graph."""
    node_id: str
    description: str
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "result:alphafold_accuracy",
                "description": "90% accuracy on protein folding",
                "metric_name": "accuracy",
                "metric_value": 0.90
            }
        }


class GraphEdge(BaseModel):
    """Edge in the knowledge graph."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: Dict[str, Any] = {}
    weight: float = 1.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "arxiv:2301.12345",
                "target_id": "author:john_doe",
                "edge_type": "AUTHORED_BY",
                "weight": 1.0
            }
        }


class QueryIntent(BaseModel):
    """Parsed user query intent."""
    original_query: str
    intent_type: str = Field(..., description="Type: search, explore, compare, trend")
    entities: List[str] = []
    relationships: List[str] = []
    time_range: Optional[tuple] = None
    max_hops: int = 2
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_query": "Which methods improved protein folding after 2020?",
                "intent_type": "search",
                "entities": ["protein folding", "methods"],
                "relationships": ["PROPOSES_METHOD"],
                "time_range": ("2020-01-01", "2025-01-01"),
                "max_hops": 2
            }
        }
