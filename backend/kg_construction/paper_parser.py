"""
Paper parsing and entity extraction using LLM.
"""

import re
from typing import List, Dict, Any, Optional
from ..models.graph_schema import PaperNode, MethodNode, DatasetNode


class PaperParser:
    """Parse papers and extract entities using LLM."""
    
    def __init__(self, llm_client=None):
        """Initialize parser with LLM client.
        
        Args:
            llm_client: Ollama client for LLM operations
        """
        self.llm_client = llm_client
    
    def extract_methods(self, paper: PaperNode) -> List[MethodNode]:
        """Extract methods/techniques mentioned in paper.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of MethodNode objects
        """
        if not self.llm_client:
            return self._extract_methods_heuristic(paper)
        
        prompt = f"""Analyze this scientific paper and extract all research methods, algorithms, and techniques mentioned.

Title: {paper.title}
Abstract: {paper.abstract}

Return a JSON array of methods with this format:
[
  {{"name": "Method Name", "description": "Brief description", "category": "category"}}
]

Only return the JSON array, no other text."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            import json
            content = response['message']['content']
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                methods_data = json.loads(json_match.group())
                methods = []
                for m in methods_data:
                    method = MethodNode(
                        node_id=f"method:{m['name'].lower().replace(' ', '_')}",
                        name=m['name'],
                        description=m.get('description', ''),
                        category=m.get('category', '')
                    )
                    methods.append(method)
                return methods
        except Exception as e:
            print(f"LLM extraction failed: {e}, using heuristic")
            return self._extract_methods_heuristic(paper)
        
        return []
    
    def _extract_methods_heuristic(self, paper: PaperNode) -> List[MethodNode]:
        """Heuristic-based method extraction (fallback).
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of MethodNode objects
        """
        # Common method keywords
        method_keywords = [
            "deep learning", "machine learning", "neural network",
            "transformer", "lstm", "gru", "cnn", "rnn",
            "reinforcement learning", "supervised learning",
            "unsupervised learning", "gradient descent",
            "backpropagation", "attention mechanism",
            "alphafold", "bert", "gpt", "resnet"
        ]
        
        text = (paper.title + " " + paper.abstract).lower()
        methods = []
        
        for keyword in method_keywords:
            if keyword in text:
                method = MethodNode(
                    node_id=f"method:{keyword.replace(' ', '_')}",
                    name=keyword.title(),
                    description=f"Mentioned in {paper.title}",
                    category="machine_learning"
                )
                methods.append(method)
        
        return methods[:5]  # Limit to top 5
    
    def extract_datasets(self, paper: PaperNode) -> List[DatasetNode]:
        """Extract datasets mentioned in paper.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of DatasetNode objects
        """
        if not self.llm_client:
            return self._extract_datasets_heuristic(paper)
        
        prompt = f"""Analyze this scientific paper and extract all datasets mentioned.

Title: {paper.title}
Abstract: {paper.abstract}

Return a JSON array of datasets with this format:
[
  {{"name": "Dataset Name", "description": "Brief description", "domain": "domain"}}
]

Only return the JSON array, no other text."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            content = response['message']['content']
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                datasets_data = json.loads(json_match.group())
                datasets = []
                for d in datasets_data:
                    dataset = DatasetNode(
                        node_id=f"dataset:{d['name'].lower().replace(' ', '_')}",
                        name=d['name'],
                        description=d.get('description', ''),
                        domain=d.get('domain', '')
                    )
                    datasets.append(dataset)
                return datasets
        except Exception as e:
            print(f"LLM extraction failed: {e}, using heuristic")
            return self._extract_datasets_heuristic(paper)
        
        return []
    
    def _extract_datasets_heuristic(self, paper: PaperNode) -> List[DatasetNode]:
        """Heuristic-based dataset extraction (fallback).
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of DatasetNode objects
        """
        # Common dataset names
        dataset_keywords = [
            "imagenet", "coco", "mnist", "cifar",
            "squad", "glue", "wikipedia", "common crawl",
            "genome", "protein data bank", "pubchem"
        ]
        
        text = (paper.title + " " + paper.abstract).lower()
        datasets = []
        
        for keyword in dataset_keywords:
            if keyword in text:
                dataset = DatasetNode(
                    node_id=f"dataset:{keyword.replace(' ', '_')}",
                    name=keyword.title(),
                    description=f"Used in {paper.title}",
                    domain="research"
                )
                datasets.append(dataset)
        
        return datasets[:3]  # Limit to top 3
    
    def extract_citations(self, paper: PaperNode) -> List[str]:
        """Extract citation IDs from paper references.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of cited paper IDs
        """
        # This would require full-text parsing
        # For now, return empty list (to be implemented with PDF parsing)
        return []
    
    def extract_institutions(self, paper: PaperNode) -> List[str]:
        """Extract institution names from author affiliations.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of institution names
        """
        # Common institution patterns
        institution_patterns = [
            r'University of \w+',
            r'\w+ University',
            r'\w+ Institute of Technology',
            r'MIT', r'Stanford', r'Harvard',
            r'Google', r'Microsoft', r'Meta', r'DeepMind'
        ]
        
        text = paper.title + " " + paper.abstract
        institutions = []
        
        for pattern in institution_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            institutions.extend(matches)
        
        return list(set(institutions))[:5]  # Unique, limit to 5
