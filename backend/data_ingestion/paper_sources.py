"""
Multi-source paper fetching from arXiv, PubMed, and Semantic Scholar.
"""

import arxiv
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from ..models.graph_schema import PaperNode


class ArxivFetcher:
    """Fetch papers from arXiv API."""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    def search(
        self,
        query: str,
        max_results: int = 100,
        categories: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PaperNode]:
        """Search arXiv for papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            categories: arXiv categories to filter (e.g., ['cs.LG', 'cs.AI'])
            start_date: Filter papers published after this date
            end_date: Filter papers published before this date
            
        Returns:
            List of PaperNode objects
        """
        # Build query with categories if specified
        if categories:
            category_query = " OR ".join([f"cat:{cat}" for cat in categories])
            full_query = f"({query}) AND ({category_query})"
        else:
            full_query = query
        
        search = arxiv.Search(
            query=full_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        for result in self.client.results(search):
            # Filter by date if specified
            if start_date and result.published < start_date:
                continue
            if end_date and result.published > end_date:
                continue
            
            # Convert to PaperNode
            paper = PaperNode(
                node_id=f"arxiv:{result.entry_id.split('/')[-1]}",
                title=result.title,
                abstract=result.summary,
                authors=[author.name for author in result.authors],
                publication_date=result.published,
                url=result.entry_id,
                pdf_url=result.pdf_url,
                categories=[cat for cat in result.categories],
                source="arxiv"
            )
            papers.append(paper)
            
            # Rate limiting
            time.sleep(0.1)
        
        return papers
    
    def fetch_by_ids(self, arxiv_ids: List[str]) -> List[PaperNode]:
        """Fetch specific papers by arXiv IDs.
        
        Args:
            arxiv_ids: List of arXiv IDs (e.g., ['2301.12345'])
            
        Returns:
            List of PaperNode objects
        """
        papers = []
        search = arxiv.Search(id_list=arxiv_ids)
        
        for result in self.client.results(search):
            paper = PaperNode(
                node_id=f"arxiv:{result.entry_id.split('/')[-1]}",
                title=result.title,
                abstract=result.summary,
                authors=[author.name for author in result.authors],
                publication_date=result.published,
                url=result.entry_id,
                pdf_url=result.pdf_url,
                categories=[cat for cat in result.categories],
                source="arxiv"
            )
            papers.append(paper)
        
        return papers


class PubMedFetcher:
    """Fetch papers from PubMed Central."""
    
    def __init__(self, email: Optional[str] = None):
        """Initialize PubMed fetcher.
        
        Args:
            email: Email for NCBI API (recommended but optional)
        """
        self.email = email or "scientific-kg@example.com"
        # Note: For production, use Biopython's Entrez module
        # This is a simplified implementation
    
    def search(
        self,
        query: str,
        max_results: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[PaperNode]:
        """Search PubMed for papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            start_date: Start date in format 'YYYY/MM/DD'
            end_date: End date in format 'YYYY/MM/DD'
            
        Returns:
            List of PaperNode objects
        """
        try:
            from Bio import Entrez
            Entrez.email = self.email
            
            # Build date filter
            date_filter = ""
            if start_date or end_date:
                start = start_date or "1900/01/01"
                end = end_date or datetime.now().strftime("%Y/%m/%d")
                date_filter = f" AND {start}:{end}[PDAT]"
            
            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=query + date_filter,
                retmax=max_results,
                sort="pub_date"
            )
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record.get("IdList", [])
            
            if not id_list:
                return []
            
            # Fetch details
            handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="medline",
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            
            papers = []
            for article in records.get("PubmedArticle", []):
                medline = article.get("MedlineCitation", {})
                article_data = medline.get("Article", {})
                
                # Extract data
                pmid = medline.get("PMID", "")
                title = article_data.get("ArticleTitle", "")
                abstract_list = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join(abstract_list) if abstract_list else ""
                
                # Extract authors
                author_list = article_data.get("AuthorList", [])
                authors = [
                    f"{a.get('ForeName', '')} {a.get('LastName', '')}".strip()
                    for a in author_list
                    if a.get('LastName')
                ]
                
                # Extract publication date
                pub_date = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                year = pub_date.get("Year", "")
                month = pub_date.get("Month", "01")
                day = pub_date.get("Day", "01")
                
                try:
                    publication_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
                except:
                    publication_date = None
                
                paper = PaperNode(
                    node_id=f"pubmed:{pmid}",
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    publication_date=publication_date,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    categories=["biomedical"],
                    source="pubmed"
                )
                papers.append(paper)
                
                time.sleep(0.34)  # NCBI rate limit: 3 requests per second
            
            return papers
            
        except ImportError:
            print("Warning: Biopython not installed. PubMed fetching disabled.")
            print("Install with: pip install biopython")
            return []
        except Exception as e:
            print(f"PubMed fetch error: {e}")
            return []


class SemanticScholarFetcher:
    """Fetch papers from Semantic Scholar API."""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Semantic Scholar fetcher.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
    
    def search(
        self,
        query: str,
        max_results: int = 100,
        fields: Optional[List[str]] = None
    ) -> List[PaperNode]:
        """Search Semantic Scholar for papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            fields: Fields to return (default: title, abstract, authors, year, url)
            
        Returns:
            List of PaperNode objects
        """
        try:
            import requests
            
            if fields is None:
                fields = ["title", "abstract", "authors", "year", "url", "citationCount"]
            
            params = {
                "query": query,
                "limit": min(max_results, 100),
                "fields": ",".join(fields)
            }
            
            response = requests.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get("data", []):
                # Extract authors
                authors = [
                    author.get("name", "")
                    for author in item.get("authors", [])
                ]
                
                # Create PaperNode
                paper = PaperNode(
                    node_id=f"s2:{item.get('paperId', '')}",
                    title=item.get("title", ""),
                    abstract=item.get("abstract", "") or "",
                    authors=authors,
                    publication_date=datetime(item.get("year", 2000), 1, 1) if item.get("year") else None,
                    url=item.get("url", ""),
                    citations_count=item.get("citationCount", 0),
                    source="semantic_scholar"
                )
                papers.append(paper)
            
            return papers
            
        except ImportError:
            print("Warning: requests library not installed.")
            print("Install with: pip install requests")
            return []
        except Exception as e:
            print(f"Semantic Scholar fetch error: {e}")
            return []


class MultiSourceFetcher:
    """Unified interface for fetching from multiple sources."""
    
    def __init__(
        self,
        pubmed_email: Optional[str] = None,
        s2_api_key: Optional[str] = None
    ):
        """Initialize multi-source fetcher.
        
        Args:
            pubmed_email: Email for PubMed API
            s2_api_key: Semantic Scholar API key
        """
        self.arxiv = ArxivFetcher()
        self.pubmed = PubMedFetcher(email=pubmed_email)
        self.semantic_scholar = SemanticScholarFetcher(api_key=s2_api_key)
    
    def search_all(
        self,
        query: str,
        max_results_per_source: int = 50,
        sources: Optional[List[str]] = None
    ) -> Dict[str, List[PaperNode]]:
        """Search all sources for papers.
        
        Args:
            query: Search query string
            max_results_per_source: Max results from each source
            sources: List of sources to search (default: all)
            
        Returns:
            Dictionary mapping source name to list of papers
        """
        if sources is None:
            sources = ["arxiv", "pubmed", "semantic_scholar"]
        
        results = {}
        
        if "arxiv" in sources:
            print(f"Searching arXiv for '{query}'...")
            results["arxiv"] = self.arxiv.search(query, max_results=max_results_per_source)
            print(f"Found {len(results['arxiv'])} papers from arXiv")
        
        if "pubmed" in sources:
            print(f"Searching PubMed for '{query}'...")
            results["pubmed"] = self.pubmed.search(query, max_results=max_results_per_source)
            print(f"Found {len(results['pubmed'])} papers from PubMed")
        
        if "semantic_scholar" in sources:
            print(f"Searching Semantic Scholar for '{query}'...")
            results["semantic_scholar"] = self.semantic_scholar.search(query, max_results=max_results_per_source)
            print(f"Found {len(results['semantic_scholar'])} papers from Semantic Scholar")
        
        return results
    
    def get_all_papers(self, results: Dict[str, List[PaperNode]]) -> List[PaperNode]:
        """Flatten results into a single list.
        
        Args:
            results: Results from search_all()
            
        Returns:
            Combined list of all papers
        """
        all_papers = []
        for papers in results.values():
            all_papers.extend(papers)
        return all_papers
