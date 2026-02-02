"""
Summary generation for exportable research reports.
Generates Markdown and structured summaries of research data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class SummaryGenerator:
    """Generate exportable summaries and reports."""
    
    def __init__(self, db_connection, llm_client=None):
        """Initialize summary generator.
        
        Args:
            db_connection: Neo4j connection
            llm_client: Optional Ollama client for narrative summaries
        """
        self.db = db_connection
        self.llm_client = llm_client
    
    def generate_topic_summary(self, topic: str, max_papers: int = 20) -> Dict[str, Any]:
        """Generate a comprehensive summary for a research topic.
        
        Args:
            topic: Research topic to summarize
            max_papers: Maximum papers to include
            
        Returns:
            Structured summary data
        """
        # Find relevant papers
        query = """
        MATCH (p:Paper)
        WHERE toLower(p.title) CONTAINS toLower($topic)
           OR toLower(p.abstract) CONTAINS toLower($topic)
           OR $topic IN [cat IN p.categories | toLower(cat)]
        OPTIONAL MATCH (p)-[:AUTHORED_BY]->(a:Author)
        OPTIONAL MATCH (p)-[:PROPOSES_METHOD|USES_METHOD]->(m:Method)
        OPTIONAL MATCH (p)-[:USES_DATASET]->(d:Dataset)
        WITH p, collect(DISTINCT a.name) AS authors,
             collect(DISTINCT m.name) AS methods,
             collect(DISTINCT d.name) AS datasets
        RETURN p.node_id AS id,
               p.title AS title,
               p.abstract AS abstract,
               p.publication_date AS date,
               p.source AS source,
               p.url AS url,
               authors, methods, datasets
        ORDER BY p.publication_date DESC
        LIMIT $max_papers
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, topic=topic, max_papers=max_papers)
                
                papers = []
                all_methods = set()
                all_datasets = set()
                all_authors = set()
                
                for record in result:
                    papers.append({
                        "id": record['id'],
                        "title": record['title'],
                        "abstract": record['abstract'][:500] if record['abstract'] else "",
                        "date": record['date'],
                        "source": record['source'],
                        "url": record['url'],
                        "authors": record['authors'],
                        "methods": record['methods'],
                        "datasets": record['datasets']
                    })
                    all_methods.update(record['methods'])
                    all_datasets.update(record['datasets'])
                    all_authors.update(record['authors'])
                
                summary = {
                    "topic": topic,
                    "generated_at": datetime.now().isoformat(),
                    "statistics": {
                        "total_papers": len(papers),
                        "unique_authors": len(all_authors),
                        "unique_methods": len(all_methods),
                        "unique_datasets": len(all_datasets)
                    },
                    "key_methods": list(all_methods)[:10],
                    "key_datasets": list(all_datasets)[:10],
                    "top_authors": list(all_authors)[:10],
                    "papers": papers
                }
                
                return summary
        except Exception as e:
            return {"error": str(e), "topic": topic}
    
    def generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """Convert summary to Markdown format.
        
        Args:
            summary: Summary data dictionary
            
        Returns:
            Markdown formatted report
        """
        if "error" in summary:
            return f"# Error\n\n{summary['error']}"
        
        md = []
        md.append(f"# Research Summary: {summary['topic']}")
        md.append(f"\n*Generated: {summary['generated_at']}*\n")
        
        # Statistics
        md.append("## Overview\n")
        stats = summary['statistics']
        md.append(f"- **Total Papers**: {stats['total_papers']}")
        md.append(f"- **Unique Authors**: {stats['unique_authors']}")
        md.append(f"- **Methods Identified**: {stats['unique_methods']}")
        md.append(f"- **Datasets Used**: {stats['unique_datasets']}")
        md.append("")
        
        # Key Methods
        if summary.get('key_methods'):
            md.append("## Key Methods\n")
            for method in summary['key_methods']:
                md.append(f"- {method}")
            md.append("")
        
        # Key Datasets
        if summary.get('key_datasets'):
            md.append("## Datasets\n")
            for dataset in summary['key_datasets']:
                md.append(f"- {dataset}")
            md.append("")
        
        # Top Authors
        if summary.get('top_authors'):
            md.append("## Top Authors\n")
            for author in summary['top_authors']:
                md.append(f"- {author}")
            md.append("")
        
        # Papers
        md.append("## Papers\n")
        for i, paper in enumerate(summary.get('papers', []), 1):
            md.append(f"### {i}. {paper['title']}\n")
            if paper.get('date'):
                md.append(f"**Date**: {paper['date']}")
            if paper.get('source'):
                md.append(f"**Source**: {paper['source']}")
            if paper.get('url'):
                md.append(f"**URL**: [{paper['url']}]({paper['url']})")
            if paper.get('authors'):
                md.append(f"**Authors**: {', '.join(paper['authors'][:5])}")
            if paper.get('abstract'):
                md.append(f"\n> {paper['abstract'][:300]}...")
            md.append("")
        
        return "\n".join(md)
    
    def generate_executive_summary(self, topic: str) -> str:
        """Generate an executive summary using LLM.
        
        Args:
            topic: Research topic
            
        Returns:
            Executive summary text
        """
        summary_data = self.generate_topic_summary(topic, max_papers=10)
        
        if "error" in summary_data:
            return f"Error generating summary: {summary_data['error']}"
        
        if not self.llm_client:
            # Return structured summary without LLM
            return self._generate_basic_executive_summary(summary_data)
        
        # Use LLM for narrative summary
        prompt = f"""Based on the following research data about "{topic}", write a concise executive summary for researchers:

Research Data:
- Total Papers Analyzed: {summary_data['statistics']['total_papers']}
- Key Methods: {', '.join(summary_data['key_methods'][:5])}
- Key Datasets: {', '.join(summary_data['key_datasets'][:5])}

Sample Paper Titles:
{chr(10).join(['- ' + p['title'] for p in summary_data['papers'][:5]])}

Write a 3-4 paragraph executive summary covering:
1. Current state of research in this area
2. Key methodological approaches
3. Data resources being utilized
4. Emerging trends or gaps

Keep it professional and insightful."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return self._generate_basic_executive_summary(summary_data)
    
    def _generate_basic_executive_summary(self, summary: Dict[str, Any]) -> str:
        """Generate basic summary without LLM.
        
        Args:
            summary: Summary data
            
        Returns:
            Basic executive summary
        """
        stats = summary['statistics']
        topic = summary['topic']
        
        text = f"""# Executive Summary: {topic}

## Overview
This analysis covers {stats['total_papers']} papers in the field of {topic}, 
involving {stats['unique_authors']} unique authors.

## Methods
The research utilizes {stats['unique_methods']} distinct methods, including:
{', '.join(summary['key_methods'][:5]) or 'No methods identified'}

## Data Resources
Researchers in this area commonly use {stats['unique_datasets']} datasets:
{', '.join(summary['key_datasets'][:5]) or 'No datasets identified'}

## Key Contributors
Leading authors in this field include:
{', '.join(summary['top_authors'][:5]) or 'No authors identified'}
"""
        return text
    
    def export_to_json(self, summary: Dict[str, Any]) -> str:
        """Export summary as JSON.
        
        Args:
            summary: Summary data
            
        Returns:
            JSON string
        """
        return json.dumps(summary, indent=2, default=str)
    
    def generate_comparison_report(
        self,
        topics: List[str],
        max_papers_per_topic: int = 10
    ) -> Dict[str, Any]:
        """Generate a comparison report across multiple topics.
        
        Args:
            topics: List of topics to compare
            max_papers_per_topic: Papers per topic
            
        Returns:
            Comparison data
        """
        summaries = {}
        for topic in topics:
            summaries[topic] = self.generate_topic_summary(topic, max_papers_per_topic)
        
        # Extract comparison metrics
        comparison = {
            "topics": topics,
            "generated_at": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for topic, summary in summaries.items():
            if "error" not in summary:
                comparison["metrics"][topic] = {
                    "paper_count": summary['statistics']['total_papers'],
                    "author_count": summary['statistics']['unique_authors'],
                    "method_count": summary['statistics']['unique_methods'],
                    "dataset_count": summary['statistics']['unique_datasets'],
                    "key_methods": summary['key_methods'][:5]
                }
        
        comparison["summaries"] = summaries
        return comparison
