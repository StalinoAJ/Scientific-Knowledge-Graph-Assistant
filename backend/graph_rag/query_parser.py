"""
Graph RAG query parser using Llama 3.2 to understand user intent.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models.graph_schema import QueryIntent


class QueryParser:
    """Parse natural language queries using LLM."""
    
    def __init__(self, llm_client):
        """Initialize query parser.
        
        Args:
            llm_client: Ollama client for LLM
        """
        self.llm_client = llm_client
    
    def parse_query(self, query: str) -> QueryIntent:
        """Parse user query and extract intent.
        
        Args:
            query: Natural language query
            
        Returns:
            QueryIntent object with parsed information
        """
        # Use fast heuristic parsing by default for speed
        # Only use LLM for complex queries
        query_lower = query.lower()
        
        # Check if this is a complex query that needs LLM parsing
        complex_indicators = ["compare", "relationship between", "how does", "why", "explain"]
        is_complex = any(indicator in query_lower for indicator in complex_indicators)
        
        if not is_complex or self.llm_client is None:
            # Fast path: use heuristic parsing
            return self._parse_heuristic(query)
        
        # Complex query: use LLM (slower but more accurate)
        prompt = f"""Analyze this query and return JSON:
Query: "{query}"
Return: {{"intent_type": "search|explore|compare|trend", "entities": [], "relationships": [], "time_range": null, "max_hops": 2}}
Only JSON, no text."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}],
                options={
                    "num_predict": 150,  # Short response needed
                    "temperature": 0.3,   # More deterministic
                    "num_ctx": 512,       # Minimal context
                }
            )
            
            content = response['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Convert time_range to tuple if present
                time_range = None
                if data.get("time_range") and isinstance(data["time_range"], list):
                    if len(data["time_range"]) == 2:
                        time_range = (data["time_range"][0], data["time_range"][1])
                
                return QueryIntent(
                    original_query=query,
                    intent_type=data.get("intent_type", "search"),
                    entities=data.get("entities", []) if data.get("entities") else [],
                    relationships=data.get("relationships", []) if data.get("relationships") else [],
                    time_range=time_range,
                    max_hops=data.get("max_hops", 2)
                )
        except Exception as e:
            print(f"LLM parse failed: {e}, using heuristic")
        
        return self._parse_heuristic(query)
    
    def _parse_heuristic(self, query: str) -> QueryIntent:
        """Fallback heuristic query parsing.
        
        Args:
            query: User query
            
        Returns:
            QueryIntent object
        """
        query_lower = query.lower()
        
        # Determine intent type
        intent_type = "search"
        if any(word in query_lower for word in ["trend", "over time", "evolution"]):
            intent_type = "trend"
        elif any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            intent_type = "compare"
        elif any(word in query_lower for word in ["explore", "related", "connected"]):
            intent_type = "explore"
        
        # Extract entities (simple keyword extraction)
        entities = []
        
        # Common research terms
        research_terms = [
            "deep learning", "machine learning", "neural network",
            "protein folding", "drug discovery", "quantum computing",
            "methods", "datasets", "algorithms", "techniques"
        ]
        
        for term in research_terms:
            if term in query_lower:
                entities.append(term)
        
        # Extract time range
        time_range = None
        year_pattern = r'(after|since|before|in)\s+(\d{4})'
        year_matches = re.findall(year_pattern, query_lower)
        
        if year_matches:
            # Simple: if "after 2020", set range from 2020 to now
            for direction, year in year_matches:
                if direction in ["after", "since"]:
                    time_range = (f"{year}-01-01", datetime.now().strftime("%Y-%m-%d"))
                    break
        
        # Determine max hops
        max_hops = 2
        if "direct" in query_lower or "immediate" in query_lower:
            max_hops = 1
        elif "indirect" in query_lower or "related" in query_lower:
            max_hops = 3
        
        return QueryIntent(
            original_query=query,
            intent_type=intent_type,
            entities=entities,
            relationships=[],
            time_range=time_range,
            max_hops=max_hops
        )
    
    def extract_search_terms(self, query_intent: QueryIntent) -> List[str]:
        """Extract search terms for semantic search.
        
        Args:
            query_intent: Parsed query intent
            
        Returns:
            List of search terms
        """
        terms = [query_intent.original_query]
        terms.extend(query_intent.entities)
        return list(set(terms))
