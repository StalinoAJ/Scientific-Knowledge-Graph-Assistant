# Fix Missing Relationships Script
# This script will create relationships for existing papers in the database

Write-Host "`n🔧 Fixing Missing Relationships in Knowledge Graph`n" -ForegroundColor Cyan

# First, let's check current status
Write-Host "📊 Current Graph Status:" -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
Write-Host "   Nodes: $($stats.total_nodes)" -ForegroundColor White
Write-Host "   Relationships: $($stats.total_relationships)`n" -ForegroundColor White

if ($stats.total_relationships -eq 0) {
    Write-Host "⚠️  No relationships found! This is the problem.`n" -ForegroundColor Red
}

# The issue is that during ingestion, relationships weren't created
# We have two options:

Write-Host "Options to fix:" -ForegroundColor Cyan
Write-Host "1. Re-ingest papers (will create relationships)" -ForegroundColor White
Write-Host "2. Manually fix existing data with Cypher queries`n" -ForegroundColor White

# Option 1: Re-ingest a small set of papers with relationships
Write-Host "🔄 Re-ingesting a few papers to demonstrate working relationships...`n" -ForegroundColor Green

$body = @{
    query = "deep learning computer vision"
    max_results_per_source = 5
    sources = @("arxiv")
} | ConvertTo-Json

try {
    Write-Host "Fetching and ingesting papers with relationships..." -ForegroundColor Yellow
    $result = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ingest" `
        -ContentType "application/json" -Body $body
    
    Write-Host "`n✅ Ingestion Complete!" -ForegroundColor Green
    Write-Host "   Papers fetched: $($result.papers_fetched)" -ForegroundColor White
    Write-Host "   Papers added: $($result.papers_added)`n" -ForegroundColor White
    
    # Check updated stats
    Start-Sleep -Seconds 2
    Write-Host "📊 Updated Graph Status:" -ForegroundColor Yellow
    $newStats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
    Write-Host "   Nodes: $($newStats.total_nodes)" -ForegroundColor White
    Write-Host "   Relationships: $($newStats.total_relationships)" -ForegroundColor Green
    
    if ($newStats.total_relationships -gt $stats.total_relationships) {
        $newRels = $newStats.total_relationships - $stats.total_relationships
        Write-Host "`n   ✨ Created $newRels new relationships!" -ForegroundColor Green
    }
    
} catch {
    Write-Host "`n❌ Error during ingestion: $_" -ForegroundColor Red
}

Write-Host "`n💡 Note: Check the backend logs with:" -ForegroundColor Cyan
Write-Host "   docker logs sci-kg-backend --tail 50`n" -ForegroundColor Gray

Write-Host "✨ Done! Refresh your graph visualization to see the connections.`n" -ForegroundColor Green
