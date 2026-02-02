# Simple Paper Ingestion Script
# Usage: .\ingest_papers.ps1

param(
    [string]$Query = "machine learning transformers",
    [int]$MaxResults = 10,
    [string[]]$Sources = @("arxiv")
)

Write-Host "`n🔍 Scientific Knowledge Graph - Paper Ingestion`n" -ForegroundColor Cyan

# Check if backend is running
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
    Write-Host "✅ Backend API is running" -ForegroundColor Green
    Write-Host "   Neo4j: $($healthCheck.services.neo4j)" -ForegroundColor Gray
    Write-Host "   Ollama: $($healthCheck.services.ollama)`n" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend API is not reachable. Please ensure Docker containers are running." -ForegroundColor Red
    Write-Host "   Run: docker-compose up -d`n" -ForegroundColor Yellow
    exit 1
}

# Display ingestion parameters
Write-Host "📋 Ingestion Parameters:" -ForegroundColor Yellow
Write-Host "   Query: $Query" -ForegroundColor White
Write-Host "   Max results per source: $MaxResults" -ForegroundColor White
Write-Host "   Sources: $($Sources -join ', ')`n" -ForegroundColor White

# Create request body
$body = @{
    query = $Query
    max_results_per_source = $MaxResults
    sources = $Sources
} | ConvertTo-Json

# Send ingestion request
Write-Host "🚀 Starting ingestion..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Method Post `
        -Uri "http://localhost:8000/ingest" `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "`n✅ Ingestion Complete!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Papers fetched: $($response.papers_fetched)" -ForegroundColor Yellow
    Write-Host "   Papers added to graph: $($response.papers_added)" -ForegroundColor Green
    Write-Host "   Message: $($response.message)`n" -ForegroundColor Gray
    
    # Get updated stats
    Write-Host "📊 Updated Graph Statistics:" -ForegroundColor Cyan
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
    Write-Host "   Total nodes: $($stats.total_nodes)" -ForegroundColor White
    Write-Host "   Total relationships: $($stats.total_relationships)" -ForegroundColor White
    Write-Host "   Papers: $($stats.nodes_by_type.Paper)" -ForegroundColor Yellow
    Write-Host "   Authors: $($stats.nodes_by_type.Author)" -ForegroundColor Yellow
    
    Write-Host "`n🎉 Success! You can now query your knowledge graph." -ForegroundColor Green
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
    Write-Host "   Neo4j Browser: http://localhost:7474`n" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Ingestion Failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)`n" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorDetails = $reader.ReadToEnd()
        Write-Host "   Details: $errorDetails`n" -ForegroundColor Yellow
    }
    exit 1
}
