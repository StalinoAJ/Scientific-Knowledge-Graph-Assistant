# Paper Ingestion Guide

This guide explains how to ingest scientific papers into your Knowledge Graph Assistant from multiple sources (arXiv, PubMed, Semantic Scholar).

## Prerequisites

Make sure all services are running:
- ✅ Neo4j: `http://localhost:7474` (healthy)
- ✅ Backend API: `http://localhost:8000` (running)
- ✅ Ollama: `http://localhost:11434` (running)
- ✅ Frontend: `http://localhost:3000` (optional)

Check services status:
```bash
docker ps
```

## Method 1: Using the REST API (Recommended)

### Basic Ingestion

Send a POST request to `/ingest` endpoint:

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning transformers",
    "max_results_per_source": 10,
    "sources": ["arxiv", "semantic_scholar"]
  }'
```

### API Parameters

- **`query`** (required): Search query string (e.g., "quantum computing", "BERT NLP")
- **`max_results_per_source`** (optional, default=20): Number of papers to fetch from each source
- **`sources`** (optional, default=all): List of sources to search
  - Available: `"arxiv"`, `"pubmed"`, `"semantic_scholar"`

### Example Queries

**Computer Science Papers:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning computer vision",
    "max_results_per_source": 20,
    "sources": ["arxiv"]
  }'
```

**Biomedical Papers:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cancer genomics",
    "max_results_per_source": 15,
    "sources": ["pubmed", "semantic_scholar"]
  }'
```

**All Sources:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "attention mechanism neural networks",
    "max_results_per_source": 10
  }'
```

### Response Format

```json
{
  "status": "success",
  "papers_fetched": 30,
  "papers_added": 28,
  "message": "Successfully ingested 28 papers from 30 fetched"
}
```

## Method 2: Using PowerShell

### Simple Request

```powershell
$body = @{
    query = "artificial intelligence"
    max_results_per_source = 15
    sources = @("arxiv", "semantic_scholar")
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ingest" `
  -ContentType "application/json" -Body $body
```

### With Progress Tracking

```powershell
# Define search query
$query = "graph neural networks"

write-host "🔍 Searching for papers about: $query" -ForegroundColor Cyan

# Create request
$body = @{
    query = $query
    max_results_per_source = 20
    sources = @("arxiv")
} | ConvertTo-Json

# Send request
$response = Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/ingest" `
  -ContentType "application/json" `
  -Body $body

# Display results
Write-Host "✅ Status: $($response.status)" -ForegroundColor Green
Write-Host "📥 Papers fetched: $($response.papers_fetched)" -ForegroundColor Yellow
Write-Host "📊 Papers added to graph: $($response.papers_added)" -ForegroundColor Green
Write-Host "💬 $($response.message)" -ForegroundColor White
```

## Method 3: Python Script

Create a Python script to ingest papers programmatically:

```python
import requests
import json

def ingest_papers(query, max_results=20, sources=None):
    """Ingest papers into the knowledge graph."""
    
    url = "http://localhost:8000/ingest"
    
    payload = {
        "query": query,
        "max_results_per_source": max_results,
        "sources": sources or ["arxiv", "semantic_scholar"]
    }
    
    print(f"🔍 Searching for: {query}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['status']}")
        print(f"📥 Fetched: {result['papers_fetched']} papers")
        print(f"📊 Added: {result['papers_added']} papers")
        print(f"💬 {result['message']}")
        return result
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

# Examples
if __name__ == "__main__":
    # Computer Science
    ingest_papers("transformer models NLP", max_results=15, sources=["arxiv"])
    
    # Biomedical
    ingest_papers("protein folding", max_results=10, sources=["pubmed"])
    
    # Multi-source
    ingest_papers("reinforcement learning robotics", max_results=20)
```

## Method 4: From within Docker Container

If you want to test from inside the backend container:

```bash
# Enter the backend container
docker exec -it sci-kg-backend bash

# Use curl inside the container
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"query": "climate change modeling", "max_results_per_source": 10}'
```

## Checking Ingestion Status

### View Graph Statistics

```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "total_nodes": 350,
  "total_relationships": 890,
  "nodes_by_type": {
    "Paper": 100,
    "Author": 230,
    "Method": 15,
    "Dataset": 5
  },
  "relationships_by_type": {
    "AUTHORED_BY": 450,
    "CITES": 320,
    "PROPOSES_METHOD": 80,
    "USES_DATASET": 40
  }
}
```

### Export Graph for Visualization

```bash
curl "http://localhost:8000/graph/export?max_nodes=100" > graph_data.json
```

## Advanced: Batch Ingestion

Create a batch script to ingest multiple topics:

```powershell
# batch_ingest.ps1
$topics = @(
    "graph neural networks",
    "attention mechanisms",
    "transformer models",
    "BERT fine-tuning",
    "vision transformers"
)

foreach ($topic in $topics) {
    Write-Host "`n🔍 Ingesting: $topic" -ForegroundColor Cyan
    
    $body = @{
        query = $topic
        max_results_per_source = 10
        sources = @("arxiv")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Method Post `
          -Uri "http://localhost:8000/ingest" `
          -ContentType "application/json" `
          -Body $body
        
        Write-Host "✅ Added $($response.papers_added) papers" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed: $_" -ForegroundColor Red
    }
    
    # Rate limiting
    Start-Sleep -Seconds 2
}

Write-Host "`n🎉 Batch ingestion complete!" -ForegroundColor Green
```

Run it:
```powershell
.\batch_ingest.ps1
```

## Source-Specific Details

### arXiv
- **Coverage**: Computer Science, Physics, Mathematics, etc.
- **Rate Limit**: Built-in (0.1s between requests)
- **Categories**: Can filter by category (e.g., `cs.LG`, `cs.AI`)

### PubMed
- **Coverage**: Biomedical and life sciences
- **Rate Limit**: 3 requests/second (handled automatically)
- **Note**: Requires Biopython (`pip install biopython`)

### Semantic Scholar
- **Coverage**: Cross-disciplinary, 200M+ papers
- **Rate Limit**: 100 requests/5 minutes (free tier)
- **API Key**: Optional, for higher limits

## What Gets Ingested?

For each paper, the system creates:

1. **Paper Node** with:
   - Title, abstract
   - Publication date
   - URL, PDF URL
   - Categories
   - Citation count
   - Embeddings (for semantic search)

2. **Author Nodes** + relationships

3. **Method Nodes** (if extracted)

4. **Dataset Nodes** (if extracted)

5. **Relationships**:
   - `AUTHORED_BY`
   - `CITES`
   - `PROPOSES_METHOD`
   - `USES_DATASET`

## Troubleshooting

### "Services not initialized" Error
- Restart the backend container:
  ```bash
  docker-compose restart backend
  ```

### "Database not connected" Error
- Check Neo4j is running:
  ```bash
  docker ps | grep neo4j
  ```
- Check backend logs:
  ```bash
  docker logs sci-kg-backend
  ```

### No Papers Found
- Try broader queries
- Check source availability
- Verify internet connection

### Rate Limiting
- Reduce `max_results_per_source`
- Add delays between requests
- Use fewer sources

## API Documentation

View full API docs at: **http://localhost:8000/docs**

This provides an interactive Swagger UI where you can test all endpoints directly from your browser.

## Next Steps

After ingesting papers:

1. **Query the Graph**: Use the `/query` endpoint or frontend
2. **Explore Relationships**: Use Neo4j Browser at `http://localhost:7474`
3. **Visualize**: Use the frontend visualization dashboard
4. **Export Data**: Use `/graph/export` for custom visualizations

Happy researching! 🔬📚
