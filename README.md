# Scientific Knowledge Graph Assistant

AI-powered research assistant that explores and understands scientific literature through an intelligent knowledge graph combining Graph RAG, LLMs, and multi-source data ingestion.

## 🚀 Features

- **Zero-Cost Architecture**: Built entirely with free, open-source tools
- **Multi-Source Ingestion**: Fetch papers from arXiv, PubMed, and Semantic Scholar
- **Graph RAG**: Semantic search + multi-hop reasoning through knowledge graphs
- **Local LLM**: Powered by Llama 3.2 via Ollama (no API costs)
- **Premium UI**: Modern React + TypeScript frontend with interactive Cytoscape.js visualization
- **Cloud-Ready**: Docker + Kubernetes deployment configurations included

## 🏗️ Architecture

### Backend
- **FastAPI**: REST API server
- **Neo4j Community Edition**: Graph database
- **Ollama + Llama 3.2**: Local LLM for query understanding and answer generation
- **Sentence Transformers**: Semantic embeddings for similarity search
- **Multi-source fetchers**: arXiv, PubMed, Semantic Scholar APIs

### Frontend
- **React + TypeScript**: Type-safe component library
- **Cytoscape.js**: Interactive graph visualization
- **Modern UI**: Dark theme with glassmorphism and smooth animations

## 📋 Prerequisites

1. **Docker & Docker Compose** (for containerized deployment)
   OR
2. **Python 3.11+** and **Node.js 20+** (for local development)
3. **Ollama** with Llama 3.2 model installed

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Install Ollama and pull Llama 3.2**:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.2
   ollama serve
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Neo4j Browser: http://localhost:7474 (login: neo4j/scientifickg123)

### Option 2: Local Development

1. **Start Neo4j**:
   ```bash
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/scientifickg123 \
     neo4j:5.15-community
   ```

2. **Install and run Ollama**:
   ```bash
   ollama pull llama3.2
   ollama serve
   ```

3. **Start Backend**:
   ```bash
   cd backend
   pip install -r ../requirements.txt
   python -m uvicorn api.server:app --reload
   ```

4. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📚 Usage

### 1. Ingest Papers

Use the `/ingest` endpoint to populate the knowledge graph:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "query": "protein folding deep learning",
    "max_results_per_source": 20,
    "sources": ["arxiv", "pubmed"]
  }'
```

### 2. Query the Knowledge Graph

Example queries:
- "Which deep learning methods improved protein folding accuracy after 2020?"
- "Show me all datasets used for drug discovery in the last five years"
- "Which institutions are leading in quantum computing research?"

## 🎨 UI Features

- **Interactive Graph Visualization**: Color-coded nodes (papers, authors, methods, datasets)
- **Smart Query Interface**: Example queries and auto-suggestions
- **Real-time Results**: Streaming answers with citations
- **Multi-hop Exploration**: Discover hidden relationships across papers
- **Dark Mode**: Premium glassmorphism design

## 🛠️ API Endpoints

- `GET /health` - Health check
- `POST /query` - Query the knowledge graph
- `POST /ingest` - Ingest papers from sources
- `GET /stats` - Get graph statistics
- `GET /graph/export` - Export graph for visualization
- `GET /paper/{paper_id}` - Get paper details

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=scientifickg123
OLLAMA_HOST=http://localhost:11434
REACT_APP_API_URL=http://localhost:8000
```

### Neo4j Configuration

The system automatically creates:
- Uniqueness constraints for all node types
- Indexes for efficient querying
- Graph algorithms support (APOC, GDS)

## 🐳 Kubernetes Deployment

Deploy to Kubernetes cluster:

```bash
kubectl apply -f k8s/
```

## 📊 Example Workflow

1. **Ingest Research Papers**:
   - Search arXiv for "quantum computing"
   - Fetch papers with metadata
   - Extract methods, datasets, authors
   - Build knowledge graph

2. **Query with Natural Language**:
   - "Which quantum algorithms were proposed at MIT?"
   - LLM parses query intent
   - Graph retrieval finds relevant papers
   - Multi-hop traversal discovers connections
   - LLM generates grounded answer

3. **Visualize Results**:
   - View knowledge graph
   - Explore paper relationships
   - Click nodes for details
   - Export findings

## 🤝 Contributing

Contributions welcome! This is a zero-cost, open-source project.

## 📝 License

MIT License - Feel free to use for research and education

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Neo4j** - Graph database
- **arXiv, PubMed, Semantic Scholar** - Paper sources
- **Cytoscape.js** - Graph visualization

---

**Note**: Make sure Ollama is running with the llama3.2 model before starting the backend. The system gracefully falls back to heuristic extraction if the LLM is unavailable.
