"""
Trend detection for scientific research patterns.
Analyzes temporal patterns in publications, methods, and research topics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json


class TrendDetector:
    """Detect trends and patterns in scientific literature."""
    
    def __init__(self, db_connection, llm_client=None):
        """Initialize trend detector.
        
        Args:
            db_connection: Neo4j connection
            llm_client: Optional Ollama client for trend analysis
        """
        self.db = db_connection
        self.llm_client = llm_client
    
    def get_publication_trends(
        self,
        time_window_days: int = 365,
        granularity: str = "month"
    ) -> Dict[str, Any]:
        """Get publication volume trends over time.
        
        Args:
            time_window_days: Number of days to analyze
            granularity: 'day', 'week', or 'month'
            
        Returns:
            Trend data with counts per time period
        """
        # Calculate date format based on granularity
        date_formats = {
            "day": "%Y-%m-%d",
            "week": "%Y-W%W",
            "month": "%Y-%m"
        }
        date_format = date_formats.get(granularity, "%Y-%m")
        
        query = """
        MATCH (p:Paper)
        WHERE p.publication_date IS NOT NULL
        WITH p, date(p.publication_date) AS pubDate
        WHERE pubDate >= date() - duration({days: $days})
        RETURN 
            pubDate.year AS year,
            pubDate.month AS month,
            pubDate.day AS day,
            count(p) AS paper_count
        ORDER BY year, month, day
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, days=time_window_days)
                
                trends = defaultdict(int)
                for record in result:
                    if granularity == "day":
                        key = f"{record['year']}-{record['month']:02d}-{record['day']:02d}"
                    elif granularity == "week":
                        # Approximate week
                        key = f"{record['year']}-W{(record['day'] // 7) + 1:02d}"
                    else:
                        key = f"{record['year']}-{record['month']:02d}"
                    trends[key] += record['paper_count']
                
                return {
                    "granularity": granularity,
                    "time_window_days": time_window_days,
                    "data": dict(sorted(trends.items()))
                }
        except Exception as e:
            return {"error": str(e), "data": {}}
    
    def get_method_trends(self, top_n: int = 10) -> Dict[str, Any]:
        """Get trending methods over time.
        
        Args:
            top_n: Number of top methods to return
            
        Returns:
            Method popularity trends
        """
        query = """
        MATCH (p:Paper)-[:PROPOSES_METHOD]->(m:Method)
        WITH m, p, date(p.publication_date) AS pubDate
        WHERE pubDate IS NOT NULL
        WITH m.name AS method_name,
             pubDate.year AS year,
             pubDate.month AS month,
             count(p) AS usage_count
        RETURN method_name, year, month, usage_count
        ORDER BY year DESC, month DESC, usage_count DESC
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query)
                
                method_trends = defaultdict(lambda: defaultdict(int))
                for record in result:
                    period = f"{record['year']}-{record['month']:02d}"
                    method_trends[record['method_name']][period] = record['usage_count']
                
                # Get top methods by total usage
                method_totals = {
                    method: sum(periods.values()) 
                    for method, periods in method_trends.items()
                }
                top_methods = sorted(method_totals.items(), key=lambda x: -x[1])[:top_n]
                
                return {
                    "top_methods": [
                        {
                            "name": method,
                            "total_papers": total,
                            "timeline": dict(sorted(method_trends[method].items()))
                        }
                        for method, total in top_methods
                    ]
                }
        except Exception as e:
            return {"error": str(e), "top_methods": []}
    
    def get_emerging_topics(self, lookback_months: int = 6) -> Dict[str, Any]:
        """Identify emerging research topics based on growth rate.
        
        Args:
            lookback_months: Months to analyze for growth
            
        Returns:
            Emerging topics with growth metrics
        """
        query = """
        MATCH (p:Paper)
        WHERE p.publication_date IS NOT NULL
        WITH p, date(p.publication_date) AS pubDate,
             p.categories AS categories
        WHERE pubDate >= date() - duration({months: $months}) AND categories IS NOT NULL
        UNWIND categories AS category
        WITH category,
             CASE WHEN pubDate >= date() - duration({months: $half_period}) 
                  THEN 'recent' ELSE 'earlier' END AS period,
             count(p) AS paper_count
        RETURN category, period, paper_count
        ORDER BY category, period
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query, months=lookback_months, half_period=lookback_months // 2)
                
                topic_data = defaultdict(lambda: {"recent": 0, "earlier": 0})
                for record in result:
                    topic_data[record['category']][record['period']] = record['paper_count']
                
                # Calculate growth rate
                emerging = []
                for topic, counts in topic_data.items():
                    if counts['earlier'] > 0:
                        growth_rate = (counts['recent'] - counts['earlier']) / counts['earlier']
                    else:
                        # Use 10.0 (1000%) as cap for new topics (0 -> N)
                        growth_rate = 10.0 if counts['recent'] > 0 else 0
                    
                    if growth_rate > 0:  # Only growing topics
                        emerging.append({
                            "topic": topic,
                            "recent_papers": counts['recent'],
                            "earlier_papers": counts['earlier'],
                            "growth_rate": round(growth_rate * 100, 1)
                        })
                
                # Sort by growth rate
                emerging.sort(key=lambda x: -x['growth_rate'])
                
                return {
                    "lookback_months": lookback_months,
                    "emerging_topics": emerging[:20]
                }
        except Exception as e:
            return {"error": str(e), "emerging_topics": []}
    
    def get_author_productivity_trends(self, top_n: int = 10) -> Dict[str, Any]:
        """Get most productive authors over time.
        
        Args:
            top_n: Number of top authors
            
        Returns:
            Author productivity data
        """
        query = """
        MATCH (a:Author)<-[:AUTHORED_BY]-(p:Paper)
        WITH a.name AS author_name,
             date(p.publication_date).year AS year,
             count(p) AS paper_count
        WHERE year IS NOT NULL
        RETURN author_name, year, paper_count
        ORDER BY paper_count DESC
        """
        
        try:
            with self.db.session() as session:
                result = session.run(query)
                
                author_data = defaultdict(lambda: defaultdict(int))
                author_totals = defaultdict(int)
                
                for record in result:
                    author_data[record['author_name']][record['year']] = record['paper_count']
                    author_totals[record['author_name']] += record['paper_count']
                
                top_authors = sorted(author_totals.items(), key=lambda x: -x[1])[:top_n]
                
                return {
                    "top_authors": [
                        {
                            "name": author,
                            "total_papers": total,
                            "by_year": dict(sorted(author_data[author].items()))
                        }
                        for author, total in top_authors
                    ]
                }
        except Exception as e:
            return {"error": str(e), "top_authors": []}
    
    def analyze_trends_with_llm(self, trend_data: Dict[str, Any]) -> str:
        """Use LLM to generate natural language trend analysis.
        
        Args:
            trend_data: Trend data to analyze
            
        Returns:
            Natural language analysis
        """
        if not self.llm_client:
            return "LLM not available for trend analysis."
        
        prompt = f"""Analyze the following research trends and provide insights:

Trend Data:
{json.dumps(trend_data, indent=2)}

Please provide:
1. Key observations about the trends
2. Notable patterns or anomalies
3. Potential implications for researchers
4. Recommendations for future research directions

Keep the analysis concise but insightful."""

        try:
            response = self.llm_client.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating analysis: {e}"
