# Batch Paper Ingestion Script
# Ingests papers from multiple topics/queries

Write-Host "`n🚀 Batch Paper Ingestion for Knowledge Graph`n" -ForegroundColor Cyan

# Define topics to ingest
$topics = @(
    @{
        query = "transformer models natural language processing"
        max_results = 15
        sources = @("arxiv", "semantic_scholar")
    },
    @{
        query = "graph neural networks"
        max_results = 10
        sources = @("arxiv")
    },
    @{
        query = "BERT fine-tuning"
        max_results = 10
        sources = @("arxiv", "semantic_scholar")
    },
    @{
        query = "attention mechanism deep learning"
        max_results = 10
        sources = @("arxiv")
    },
    @{
        query = "vision transformers"
        max_results = 10
        sources = @("arxiv")
    }
)

# Statistics
$totalFetched = 0
$totalAdded = 0
$successCount = 0
$failCount = 0

# Process each topic
foreach ($i in 0..($topics.Count - 1)) {
    $topic = $topics[$i]
    
    Write-Host "[$($i + 1)/$($topics.Count)] Processing: $($topic.query)" -ForegroundColor Yellow
    
    $body = @{
        query = $topic.query
        max_results_per_source = $topic.max_results
        sources = $topic.sources
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Method Post `
            -Uri "http://localhost:8000/ingest" `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        $totalFetched += $response.papers_fetched
        $totalAdded += $response.papers_added
        $successCount++
        
        Write-Host "  ✅ Added $($response.papers_added)/$($response.papers_fetched) papers" -ForegroundColor Green
        
    } catch {
        $failCount++
        Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Rate limiting - be nice to APIs
    if ($i -lt ($topics.Count - 1)) {
        Write-Host "  ⏳ Waiting 3 seconds...`n" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

# Final summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "📊 Batch Ingestion Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Topics processed: $successCount/$($topics.Count)" -ForegroundColor White
Write-Host "Total papers fetched: $totalFetched" -ForegroundColor Yellow
Write-Host "Total papers added: $totalAdded" -ForegroundColor Green
Write-Host "Failed topics: $failCount`n" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })

# Get final graph stats
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
    Write-Host "🎯 Current Graph Statistics:" -ForegroundColor Cyan
    Write-Host "   Total nodes: $($stats.total_nodes)" -ForegroundColor White
    Write-Host "   Total relationships: $($stats.total_relationships)" -ForegroundColor White
    
    if ($stats.nodes_by_type) {
        Write-Host "`n   Nodes by type:" -ForegroundColor Gray
        foreach ($nodeType in $stats.nodes_by_type.PSObject.Properties) {
            Write-Host "     - $($nodeType.Name): $($nodeType.Value)" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "⚠️  Could not fetch final statistics" -ForegroundColor Yellow
}

Write-Host "`n✨ Batch ingestion complete!`n" -ForegroundColor Green
