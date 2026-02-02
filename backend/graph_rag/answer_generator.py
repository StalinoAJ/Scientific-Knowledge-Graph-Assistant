"""
Answer generation using Llama 3.2 with retrieved graph context.
"""

from typing import Dict, Any, List, Optional
import json


class AnswerGenerator:
    """Generate natural language answers using LLM with graph context."""
    
    def __init__(self, llm_client):
        """Initialize answer generator.
        
        Args:
            llm_client: Ollama client
        """
        self.llm_client = llm_client
    
    def format_context(self, graph_context: Dict[str, Any]) -> str:
        """Format graph context into readable text for LLM.
        
        Args:
            graph_context: Retrieved graph context
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add top search results - show more if it's a listing query
        if "search_results" in graph_context:
            search_results = graph_context["search_results"]
            # Show more results if there are many (likely a listing query)
            max_results = min(len(search_results), 25)  # Show up to 25 papers
            
            context_parts.append(f"=== Papers ({len(search_results)} found) ===")
            for i, result in enumerate(search_results[:max_results], 1):
                # Shorter format for listings
                title = result.get('title', 'Unknown')
                node_id = result.get('node_id', '')
                abstract = result.get('abstract', '')
                
                if max_results > 10:
                    # Brief format for long lists
                    context_parts.append(f"{i}. {title} (ID: {node_id})")
                else:
                    # Detailed format for shorter lists
                    abstract_preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
                    context_parts.append(
                        f"{i}. {title} (ID: {node_id})\n"
                        f"   {abstract_preview}"
                    )
        
        # Add connected nodes information
        if "nodes" in graph_context:
            # Group nodes by type
            nodes_by_type = {}
            for node in graph_context["nodes"]:
                node_type = node["type"]
                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []
                nodes_by_type[node_type].append(node)
            
            # Format each type
            for node_type, nodes in nodes_by_type.items():
                if nodes:
                    context_parts.append(f"\n=== {node_type}s in Graph ===")
                    for node in nodes[:10]:  # Increased from 5 to 10
                        props = node.get("properties", {})
                        if node_type == "Paper":
                            context_parts.append(
                                f"- {props.get('title', 'Unknown')} ({node['id']})"
                            )
                        elif node_type == "Author":
                            context_parts.append(
                                f"- {props.get('name', 'Unknown')}"
                            )
                        elif node_type == "Method":
                            context_parts.append(
                                f"- {props.get('name', 'Unknown')}: {props.get('description', '')[:100]}"
                            )
                        elif node_type == "Dataset":
                            context_parts.append(
                                f"- {props.get('name', 'Unknown')}: {props.get('description', '')[:100]}"
                            )
        
        # Add relationships
        if "edges" in graph_context and graph_context["edges"]:
            context_parts.append("\n=== Key Relationships ===")
            for edge in graph_context["edges"][:15]:  # Increased from 10 to 15
                context_parts.append(
                    f"- {edge['source']} --[{edge['type']}]--> {edge['target']}"
                )
        
        return "\n".join(context_parts)
    
    def generate_answer(
        self,
        query: str,
        graph_context: Dict[str, Any],
        stream: bool = False
    ) -> str:
        """Generate answer using LLM with graph context.
        
        Args:
            query: Original user query
            graph_context: Retrieved graph context
            stream: Whether to stream the response
            
        Returns:
            Generated answer
        """
        # Format context
        formatted_context = self.format_context(graph_context)
        
        # Build prompt
        prompt = f"""You are a scientific research assistant with access to a knowledge graph of scientific literature. Answer the user's question based on the provided context from the knowledge graph.

Context from Knowledge Graph:
{formatted_context}

User Question: {query}

Instructions:
1. Use ONLY the information provided in the context
2. Cite specific papers by title when making claims
3. If the context doesn't contain enough information, say so
4. Structure your answer clearly with sections if needed
5. Include relevant paper IDs for citations

Answer:"""

        try:
            if stream:
                # Return generator for streaming
                return self._generate_streaming(prompt)
            else:
                # Non-streaming response
                response = self.llm_client.chat(
                    model="llama3.2",
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "num_predict": 1024,      # Increased from 512 to handle longer lists
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_ctx": 4096,          # Increased from 2048 for larger context
                    }
                )
                
                return response['message']['content']
                
        except Exception as e:
            return f"Error generating answer: {e}\n\nPlease ensure Ollama is running with the llama3.2 model."
    
    def _generate_streaming(self, prompt: str):
        """Internal method for streaming responses."""
        response = self.llm_client.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={
                "num_predict": 1024,
                "temperature": 0.7,
                "num_ctx": 4096,
            }
        )
        
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    
    def generate_summary(self, papers: List[Dict[str, Any]], topic: str) -> str:
        """Generate a summary of multiple papers on a topic.
        
        Args:
            papers: List of paper dictionaries
            topic: Topic to summarize
            
        Returns:
            Summary text
        """
        papers_context = "\n\n".join([
            f"Title: {p.get('title', 'Unknown')}\n"
            f"Abstract: {p.get('abstract', 'No abstract')[:300]}..."
            for p in papers[:10]
        ])
        
        prompt = f"""Summarize the key findings and trends from these scientific papers on the topic of "{topic}".

Papers:
{papers_context}

Provide a concise summary highlighting:
1. Main research directions
2. Key methods or techniques
3. Important findings
4. Common themes

Summary:"""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def extract_citations(self, answer: str) -> List[str]:
        """Extract paper IDs mentioned in the answer.
        
        Args:
            answer: Generated answer text
            
        Returns:
            List of paper IDs
        """
        import re
        
        # Match patterns like arxiv:1234.5678, pubmed:12345, s2:abc123
        pattern = r'(arxiv|pubmed|s2):[\w\.-]+'
        citations = re.findall(pattern, answer, re.IGNORECASE)
        
        return list(set(citations))
