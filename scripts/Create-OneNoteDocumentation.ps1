# Create-OneNoteDocumentation.ps1
# Creates HTML files that can be imported into OneNote
# This approach works with all versions of OneNote including OneNote for Windows 10/11

param(
    [string]$OutputPath = ".\OneNote_Documentation"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OneNote Documentation Generator" -ForegroundColor Cyan
Write-Host "  Scientific Knowledge Graph Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
$fullPath = Join-Path (Get-Location) $OutputPath
if (-not (Test-Path $fullPath)) {
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
}
Write-Host "[OK] Output directory: $fullPath" -ForegroundColor Green
Write-Host ""

# HTML template
function New-OneNoteHtml {
    param(
        [string]$Title,
        [string]$Content
    )
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>$Title</title>
    <style>
        body { font-family: 'Segoe UI', Calibri, Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #2b579a; border-bottom: 2px solid #2b579a; padding-bottom: 10px; }
        h2 { color: #4472c4; margin-top: 30px; }
        h3 { color: #5b9bd5; margin-top: 20px; }
        .section { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .highlight { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }
        .success { color: #28a745; }
        .pending { color: #dc3545; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        ul, ol { margin-left: 20px; }
        li { margin: 5px 0; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #2b579a; color: white; }
    </style>
</head>
<body>
$Content
</body>
</html>
"@
    return $html
}

# Section 1: Abstract
$abstractHtml = @"
<h1>1. Abstract</h1>

<div class="section">
<p><strong>The Scientific Knowledge Graph Assistant</strong> is an AI-powered research tool designed to explore and understand scientific literature through an intelligent knowledge graph.</p>
</div>

<p>This system combines <strong>Graph RAG</strong> (Retrieval-Augmented Generation), <strong>Large Language Models</strong> (LLMs), and <strong>multi-source data ingestion</strong> to provide researchers with deeper, context-aware insights into scientific publications.</p>

<h2>Key Highlights</h2>
<ul>
    <li><strong>Zero-cost architecture</strong> using open-source tools</li>
    <li><strong>Multi-source ingestion</strong> from arXiv, PubMed, and Semantic Scholar</li>
    <li><strong>Graph-based retrieval</strong> with multi-hop reasoning</li>
    <li><strong>Local LLM</strong> powered by Llama 3.2 via Ollama</li>
    <li><strong>Interactive visualization</strong> dashboard with Cytoscape.js</li>
    <li><strong>Cloud-ready deployment</strong> with Docker and Kubernetes</li>
</ul>

<div class="highlight">
<p><strong>Project Status:</strong> Fully functional with all core features implemented.</p>
</div>
"@

# Section 2: Introduction
$introHtml = @"
<h1>2. Introduction</h1>

<h2>Background</h2>
<p>Scientific research is growing exponentially, with millions of papers published annually across various domains. Researchers face significant challenges in:</p>
<ul>
    <li>Keeping up with the latest developments in their field</li>
    <li>Discovering connections between different research areas</li>
    <li>Understanding the evolution of methods and techniques</li>
    <li>Finding relevant datasets and collaborators</li>
</ul>

<h2>Motivation</h2>
<p>Traditional search engines and RAG systems fall short because they:</p>
<ul>
    <li>Treat documents as isolated entities</li>
    <li>Miss the rich relationships between papers, authors, and concepts</li>
    <li>Cannot perform multi-hop reasoning across the literature</li>
    <li>Lack visual exploration capabilities</li>
</ul>

<h2>Our Approach</h2>
<p>The Scientific Knowledge Graph Assistant addresses these limitations by:</p>
<ol>
    <li>Constructing a knowledge graph from scientific literature</li>
    <li>Using Graph RAG for context-aware retrieval</li>
    <li>Enabling multi-hop reasoning across papers and entities</li>
    <li>Providing interactive visualization for exploration</li>
</ol>

<h2>Target Users</h2>
<ul>
    <li>Research scientists and academics</li>
    <li>PhD students exploring literature</li>
    <li>Research teams tracking developments</li>
    <li>Science journalists and communicators</li>
</ul>
"@

# Section 3: Objectives
$objectivesHtml = @"
<h1>3. Objectives</h1>

<h2>Primary Objectives</h2>

<h3>1. Zero-Cost Deployment</h3>
<ul>
    <li>Use only free, open-source tools</li>
    <li>No API costs or subscription fees</li>
    <li>Self-hosted local LLM capability</li>
</ul>

<h3>2. Multi-Source Data Ingestion</h3>
<ul>
    <li>Integrate with arXiv for CS/Physics/Math papers</li>
    <li>Connect to PubMed for biomedical literature</li>
    <li>Access Semantic Scholar for cross-disciplinary coverage</li>
</ul>

<h3>3. Knowledge Graph Construction</h3>
<ul>
    <li>Extract entities: Papers, Authors, Methods, Datasets</li>
    <li>Create relationships: AUTHORED_BY, CITES, PROPOSES_METHOD, USES_DATASET</li>
    <li>Store embeddings for semantic search</li>
</ul>

<h3>4. Graph RAG Implementation</h3>
<ul>
    <li>Natural language query understanding</li>
    <li>Hybrid retrieval (vector + graph)</li>
    <li>Multi-hop reasoning across entities</li>
    <li>Grounded answer generation with citations</li>
</ul>

<h3>5. Interactive Visualization</h3>
<ul>
    <li>Force-directed graph layout</li>
    <li>Node filtering and search</li>
    <li>Click-to-explore functionality</li>
    <li>Real-time graph updates</li>
</ul>

<h3>6. Cloud-Ready Architecture</h3>
<ul>
    <li>Docker containerization</li>
    <li>Kubernetes deployment support</li>
    <li>Scalable microservices design</li>
</ul>
"@

# Section 4: Literature Review
$literatureHtml = @"
<h1>4. Literature Review</h1>

<h2>Related Work and Technologies</h2>

<h3>Graph RAG Approaches</h3>
<ul>
    <li><strong>Microsoft GraphRAG (2024)</strong>: Framework building community summaries from graphs</li>
    <li>This project shares the "Graph + Vector" philosophy</li>
    <li>Key paper: Edge, D., et al. "From Local to Global: A Graph RAG Approach"</li>
</ul>

<h3>Knowledge Graph Systems</h3>
<ul>
    <li><strong>Open Knowledge Maps</strong>: Visual interface for scientific topics</li>
    <li><strong>Causaly</strong>: AI platform for biomedical research with massive KG</li>
    <li>Our system adds generative AI layer on top of visualization</li>
</ul>

<h3>Retrieval-Augmented Generation</h3>
<ul>
    <li>Pan, S., et al. (2024): "Retrieval-Augmented Generation with Graphs" (Survey)</li>
    <li>Wang, X., et al. (2023): "Knowledge Graph-Enhanced RAG for QA"</li>
</ul>

<h2>Technologies Used</h2>

<table>
    <tr><th>Component</th><th>Technology</th><th>Purpose</th></tr>
    <tr><td>Backend</td><td>FastAPI</td><td>Modern Python web framework</td></tr>
    <tr><td>Database</td><td>Neo4j Community</td><td>Graph database</td></tr>
    <tr><td>LLM</td><td>Ollama + Llama 3.2</td><td>Local LLM inference</td></tr>
    <tr><td>Embeddings</td><td>Sentence Transformers</td><td>Semantic embeddings</td></tr>
    <tr><td>Frontend</td><td>React + TypeScript</td><td>UI framework</td></tr>
    <tr><td>Visualization</td><td>Cytoscape.js</td><td>Graph visualization</td></tr>
    <tr><td>Infrastructure</td><td>Docker, Kubernetes</td><td>Containerization</td></tr>
</table>
"@

# Section 5: Proposed System
$proposedHtml = @"
<h1>5. Proposed System</h1>

<h2>System Architecture</h2>

<div class="section">
<pre>
USER/BROWSER
     |
     v
NGINX REVERSE PROXY
     |
     +---> FASTAPI BACKEND ---> NEO4J GRAPH DATABASE
     |           |
     |           +---> OLLAMA LLM SERVICE
     |
     +---> REACT FRONTEND
</pre>
</div>

<h2>Graph Schema</h2>

<h3>Nodes</h3>
<ul>
    <li><strong>Paper</strong> (title, abstract, date, url, embedding)</li>
    <li><strong>Author</strong> (name, affiliation)</li>
    <li><strong>Method</strong> (name, description)</li>
    <li><strong>Dataset</strong> (name, description)</li>
</ul>

<h3>Relationships</h3>
<ul>
    <li>(Paper)-[:AUTHORED_BY]->(Author)</li>
    <li>(Paper)-[:CITES]->(Paper)</li>
    <li>(Paper)-[:PROPOSES_METHOD]->(Method)</li>
    <li>(Paper)-[:USES_DATASET]->(Dataset)</li>
</ul>

<h2>Data Flow</h2>
<ol>
    <li>User submits natural language query</li>
    <li>Query Parser extracts intent and entities</li>
    <li>Graph Retriever performs hybrid search</li>
    <li>Multi-hop traversal gathers context</li>
    <li>Answer Generator produces grounded response</li>
</ol>
"@

# Section 6: Implementation
$implementationHtml = @"
<h1>6. Implementation</h1>

<h2>Project Structure</h2>

<pre>
scientific-kg-assistant/
├── backend/
│   ├── api/server.py              # FastAPI server
│   ├── graph_rag/
│   │   ├── query_parser.py        # NL query parsing
│   │   ├── graph_retriever.py     # Semantic + graph search
│   │   └── answer_generator.py    # LLM answer generation
│   ├── kg_construction/           # Graph builder
│   ├── data_ingestion/            # Multi-source fetchers
│   ├── analytics/                 # Trends, clusters
│   └── models/                    # Database, schemas
├── frontend/src/
│   ├── App.tsx                    # Main application
│   ├── components/                # React components
│   └── services/                  # API client
├── docker-compose.yml
└── k8s/                           # Kubernetes manifests
</pre>

<h2>Key Components</h2>

<h3>Graph Retriever</h3>
<ul>
    <li><code>semantic_search()</code>: Vector similarity search</li>
    <li><code>multi_hop_traversal()</code>: Graph exploration</li>
    <li><code>retrieve_context()</code>: Full context assembly</li>
</ul>

<h3>Answer Generator</h3>
<ul>
    <li><code>format_context()</code>: Prepare graph context for LLM</li>
    <li><code>generate_answer()</code>: LLM inference with citations</li>
    <li><code>generate_summary()</code>: Multi-paper summaries</li>
</ul>

<h3>API Endpoints</h3>
<table>
    <tr><th>Endpoint</th><th>Method</th><th>Purpose</th></tr>
    <tr><td>/query</td><td>POST</td><td>Natural language queries</td></tr>
    <tr><td>/ingest</td><td>POST</td><td>Paper ingestion</td></tr>
    <tr><td>/graph/export</td><td>GET</td><td>Visualization data</td></tr>
    <tr><td>/stats</td><td>GET</td><td>Graph statistics</td></tr>
</table>
"@

# Section 7: Results & Analysis
$resultsHtml = @"
<h1>7. Results & Analysis</h1>

<h2>System Capabilities</h2>

<h3>Paper Ingestion <span class="success">✓ Complete</span></h3>
<ul>
    <li>Successfully ingests papers from multiple sources</li>
    <li>Extracts entities (authors, methods, datasets)</li>
    <li>Creates knowledge graph with relationships</li>
    <li>Generates embeddings for semantic search</li>
</ul>

<h3>Query Processing <span class="success">✓ Complete</span></h3>
<ul>
    <li>Natural language query understanding</li>
    <li>Multi-hop reasoning across papers</li>
    <li>Citation-backed answers</li>
    <li>Context-aware responses</li>
</ul>

<h3>Visualization <span class="success">✓ Complete</span></h3>
<ul>
    <li>Interactive force-directed graph layout</li>
    <li>Node filtering by type</li>
    <li>Search with real-time filtering</li>
    <li>Click-to-explore navigation</li>
</ul>

<h2>Performance</h2>
<table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Simple query response</td><td>2-5 seconds</td></tr>
    <tr><td>Complex multi-hop query</td><td>5-15 seconds</td></tr>
    <tr><td>Papers indexed</td><td>100+ nodes</td></tr>
    <tr><td>Authors tracked</td><td>200+ nodes</td></tr>
    <tr><td>Total relationships</td><td>500+ edges</td></tr>
</table>

<h2>Limitations</h2>
<ul>
    <li>Lightweight Ollama model has context limitations</li>
    <li>Large graphs may need pagination</li>
    <li>Real-time ingestion of very large datasets is slow</li>
</ul>
"@

# Section 8: Conclusion
$conclusionHtml = @"
<h1>8. Conclusion</h1>

<p>The Scientific Knowledge Graph Assistant successfully demonstrates the power of combining knowledge graphs with large language models for scientific literature exploration.</p>

<h2>Key Achievements</h2>

<div class="section">
<h3><span class="success">✓</span> Zero-Cost Architecture</h3>
<p>Built entirely with free, open-source tools including Neo4j Community, Ollama, and React.</p>

<h3><span class="success">✓</span> Graph RAG Implementation</h3>
<p>Successfully implemented hybrid retrieval combining vector similarity with graph traversal.</p>

<h3><span class="success">✓</span> Multi-Source Integration</h3>
<p>Unified ingestion pipeline for arXiv, PubMed, and Semantic Scholar.</p>

<h3><span class="success">✓</span> Interactive Visualization</h3>
<p>Modern, premium UI with Cytoscape.js enabling intuitive graph exploration.</p>

<h3><span class="success">✓</span> Cloud-Ready Deployment</h3>
<p>Docker and Kubernetes configurations for scalable deployment.</p>
</div>

<h2>Value Proposition</h2>
<table>
    <tr><th>For Researchers</th><th>For Organizations</th></tr>
    <tr><td>Discover hidden connections</td><td>No ongoing API costs</td></tr>
    <tr><td>Track method evolution</td><td>Self-hosted for privacy</td></tr>
    <tr><td>Find collaborators</td><td>Customizable and extensible</td></tr>
</table>
"@

# Section 9: Future Work
$futureHtml = @"
<h1>9. Future Work</h1>

<h2>Planned Enhancements</h2>

<h3>Improved LLM Capabilities</h3>
<ul>
    <li>Support for larger context windows</li>
    <li>Integration with more powerful local models</li>
    <li>Fine-tuning on scientific literature</li>
</ul>

<h3>Advanced Analytics</h3>
<ul>
    <li>Temporal graph analysis</li>
    <li>Predictive trend modeling</li>
    <li>Citation impact prediction</li>
    <li>Research gap identification</li>
</ul>

<h3>Visualization Improvements</h3>
<ul>
    <li>Keyboard shortcuts</li>
    <li>Export graph as image/PDF</li>
    <li>Save/load custom layouts</li>
    <li>Node clustering for large graphs</li>
    <li>Time-based filtering</li>
    <li>Minimap navigation</li>
</ul>

<h3>Additional Data Sources</h3>
<ul>
    <li>IEEE Xplore integration</li>
    <li>Google Scholar support</li>
    <li>PDF upload and processing</li>
    <li>BibTeX import</li>
</ul>

<h3>Collaboration Features</h3>
<ul>
    <li>Shared notebooks</li>
    <li>Team annotations</li>
    <li>Export to reference managers</li>
</ul>
"@

# Section 10: Current Progress
$progressHtml = @"
<h1>10. Current Progress</h1>

<h2>Completed Features</h2>

<table>
    <tr><th>Component</th><th>Feature</th><th>Status</th></tr>
    <tr><td>Core System</td><td>FastAPI backend with REST API</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Core System</td><td>Neo4j graph database integration</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Core System</td><td>Ollama LLM service connection</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Data Ingestion</td><td>arXiv, PubMed, Semantic Scholar</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Graph RAG</td><td>Query parser with intent detection</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Graph RAG</td><td>Semantic search with embeddings</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Graph RAG</td><td>Multi-hop graph traversal</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Frontend</td><td>React + TypeScript application</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Frontend</td><td>Cytoscape.js visualization</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Analytics</td><td>Publication trend detection</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Deployment</td><td>Docker Compose configuration</td><td><span class="success">✓ Done</span></td></tr>
    <tr><td>Deployment</td><td>Kubernetes manifests</td><td><span class="success">✓ Done</span></td></tr>
</table>

<h2>In Progress</h2>
<ul>
    <li>Performance optimization for large queries</li>
    <li>Enhanced error handling</li>
</ul>

<h2>Pending</h2>
<ul>
    <li class="pending">Cloud deployment</li>
</ul>
"@

# Section 11: References
$referencesHtml = @"
<h1>11. References</h1>

<h2>Research Papers</h2>
<ol>
    <li>Edge, D., Trinh, H., Cheng, N., Bradley, J., et al. (2024). <em>"From Local to Global: A Graph RAG Approach to Query-Focused Summarization."</em> Microsoft Research. arXiv:2404.16130</li>
    <li>Pan, S., Luo, L., Wang, Y., Chen, C., et al. (2024). <em>"Retrieval-Augmented Generation with Graphs."</em> arXiv:2404.02000</li>
    <li>Wang, X., et al. (2023). <em>"Knowledge Graph-Enhanced Retrieval-Augmented Generation for Accurate Question Answering."</em></li>
</ol>

<h2>Technologies</h2>
<table>
    <tr><th>Technology</th><th>URL</th></tr>
    <tr><td>Neo4j Graph Database</td><td>https://neo4j.com/</td></tr>
    <tr><td>Ollama</td><td>https://ollama.ai/</td></tr>
    <tr><td>FastAPI</td><td>https://fastapi.tiangolo.com/</td></tr>
    <tr><td>React</td><td>https://react.dev/</td></tr>
    <tr><td>Cytoscape.js</td><td>https://js.cytoscape.org/</td></tr>
    <tr><td>Sentence Transformers</td><td>https://www.sbert.net/</td></tr>
</table>

<h2>Data Sources</h2>
<table>
    <tr><th>Source</th><th>URL</th></tr>
    <tr><td>arXiv</td><td>https://arxiv.org/</td></tr>
    <tr><td>PubMed</td><td>https://pubmed.ncbi.nlm.nih.gov/</td></tr>
    <tr><td>Semantic Scholar</td><td>https://www.semanticscholar.org/</td></tr>
</table>

<h2>Project Documentation</h2>
<ul>
    <li>docs/project_documentation.md</li>
    <li>docs/INGESTION_GUIDE.md</li>
    <li>docs/GRAPH_NAVIGATION_GUIDE.md</li>
    <li>docs/DEPLOYMENT_GUIDE.md</li>
    <li>README.md</li>
</ul>
"@

# Create all HTML files
$sections = @(
    @{ Name = "01_Abstract"; Title = "Abstract"; Content = $abstractHtml },
    @{ Name = "02_Introduction"; Title = "Introduction"; Content = $introHtml },
    @{ Name = "03_Objectives"; Title = "Objectives"; Content = $objectivesHtml },
    @{ Name = "04_Literature_Review"; Title = "Literature Review"; Content = $literatureHtml },
    @{ Name = "05_Proposed_System"; Title = "Proposed System"; Content = $proposedHtml },
    @{ Name = "06_Implementation"; Title = "Implementation"; Content = $implementationHtml },
    @{ Name = "07_Results_Analysis"; Title = "Results and Analysis"; Content = $resultsHtml },
    @{ Name = "08_Conclusion"; Title = "Conclusion"; Content = $conclusionHtml },
    @{ Name = "09_Future_Work"; Title = "Future Work"; Content = $futureHtml },
    @{ Name = "10_Current_Progress"; Title = "Current Progress"; Content = $progressHtml },
    @{ Name = "11_References"; Title = "References"; Content = $referencesHtml }
)

Write-Host "Creating HTML files for OneNote import..." -ForegroundColor Yellow
Write-Host ""

foreach ($section in $sections) {
    $filePath = Join-Path $fullPath "$($section.Name).html"
    $html = New-OneNoteHtml -Title $section.Title -Content $section.Content
    $html | Out-File -FilePath $filePath -Encoding UTF8
    Write-Host "  [OK] Created: $($section.Name).html" -ForegroundColor Green
}

# Create index file
$indexContent = @"
<h1>Scientific Knowledge Graph Assistant</h1>
<h2>Documentation Index</h2>
<p>This documentation notebook contains comprehensive information about the Scientific Knowledge Graph Assistant project.</p>
<h3>Sections</h3>
<ol>
    <li><a href="01_Abstract.html">Abstract</a></li>
    <li><a href="02_Introduction.html">Introduction</a></li>
    <li><a href="03_Objectives.html">Objectives</a></li>
    <li><a href="04_Literature_Review.html">Literature Review</a></li>
    <li><a href="05_Proposed_System.html">Proposed System</a></li>
    <li><a href="06_Implementation.html">Implementation</a></li>
    <li><a href="07_Results_Analysis.html">Results and Analysis</a></li>
    <li><a href="08_Conclusion.html">Conclusion</a></li>
    <li><a href="09_Future_Work.html">Future Work</a></li>
    <li><a href="10_Current_Progress.html">Current Progress</a></li>
    <li><a href="11_References.html">References</a></li>
</ol>
<hr>
<p><em>Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm")</em></p>
"@
$indexHtml = New-OneNoteHtml -Title "Scientific Knowledge Graph Assistant - Index" -Content $indexContent
$indexHtml | Out-File -FilePath (Join-Path $fullPath "00_Index.html") -Encoding UTF8
Write-Host "  [OK] Created: 00_Index.html" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  [SUCCESS] Documentation Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output folder: $fullPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "HOW TO IMPORT INTO ONENOTE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Method 1 - OneNote Desktop:" -ForegroundColor White
Write-Host "  1. Open OneNote" -ForegroundColor Gray
Write-Host "  2. Create a new notebook or section" -ForegroundColor Gray
Write-Host "  3. Go to Insert > File Printout" -ForegroundColor Gray
Write-Host "  4. Select the HTML files from: $fullPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Method 2 - Drag and Drop:" -ForegroundColor White
Write-Host "  1. Open the folder: $fullPath" -ForegroundColor Gray
Write-Host "  2. Open OneNote and create a new section" -ForegroundColor Gray
Write-Host "  3. Drag each HTML file into OneNote" -ForegroundColor Gray
Write-Host ""
Write-Host "Method 3 - Open in Browser then Copy:" -ForegroundColor White
Write-Host "  1. Double-click an HTML file to open in browser" -ForegroundColor Gray
Write-Host "  2. Select All (Ctrl+A) and Copy (Ctrl+C)" -ForegroundColor Gray
Write-Host "  3. Paste into OneNote (Ctrl+V)" -ForegroundColor Gray
Write-Host ""

# Open the output folder
Write-Host "Opening output folder..." -ForegroundColor Yellow
Start-Process explorer.exe -ArgumentList $fullPath
