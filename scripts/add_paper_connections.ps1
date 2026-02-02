# Add Paper-to-Paper Connections
# This script creates CITES, SIMILAR_TO, and SHARES_AUTHOR relationships between papers

Write-Host "`n🔗 Adding Paper-to-Paper Connections...`n" -ForegroundColor Cyan

# 1. Add SIMILAR_TO relationships based on shared methods/datasets
Write-Host "Creating SIMILAR_TO relationships based on shared methods and datasets..." -ForegroundColor Yellow

$query1 = @"
// Papers that use the same method are similar
MATCH (p1:Paper)-[:PROPOSES_METHOD]->(m:Method)<-[:PROPOSES_METHOD]-(p2:Paper)
WHERE p1.node_id < p2.node_id
WITH p1, p2, count(m) AS shared_methods
WHERE shared_methods >= 1
MERGE (p1)-[r:SIMILAR_TO]-(p2)
SET r.reason = 'shared_methods',
    r.strength = shared_methods * 0.3
RETURN count(r) AS similar_method_links
"@

docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 $query1

# 2. Add SIMILAR_TO relationships based on shared datasets
Write-Host "`nCreating SIMILAR_TO relationships based on shared datasets..." -ForegroundColor Yellow

$query2 = @"
// Papers that use the same dataset are similar
MATCH (p1:Paper)-[:USES_DATASET]->(d:Dataset)<-[:USES_DATASET]-(p2:Paper)
WHERE p1.node_id < p2.node_id
WITH p1, p2, count(d) AS shared_datasets
WHERE shared_datasets >= 1
MERGE (p1)-[r:SIMILAR_TO]-(p2)
ON CREATE SET r.reason = 'shared_datasets', r.strength = shared_datasets * 0.4
ON MATCH SET r.strength = r.strength + (shared_datasets * 0.4)
RETURN count(r) AS similar_dataset_links
"@

docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 $query2

# 3. Add SHARES_AUTHOR relationships
Write-Host "`nCreating SHARES_AUTHOR relationships..." -ForegroundColor Yellow

$query3 = @"
// Papers by the same author(s)
MATCH (p1:Paper)-[:AUTHORED_BY]->(a:Author)<-[:AUTHORED_BY]-(p2:Paper)
WHERE p1.node_id < p2.node_id
WITH p1, p2, collect(a.name) AS shared_authors, count(a) AS author_count
WHERE author_count >= 1
MERGE (p1)-[r:SHARES_AUTHOR]-(p2)
SET r.authors = shared_authors,
    r.count = author_count
RETURN count(r) AS shared_author_links
"@

docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 $query3

# 4. Add RELATED_TOPIC relationships for papers in same field
Write-Host "`nCreating RELATED_TOPIC relationships..." -ForegroundColor Yellow

$query4 = @"
// Papers from same source with similar topics (basic heuristic)
MATCH (p1:Paper), (p2:Paper)
WHERE p1.node_id < p2.node_id
AND p1.source = p2.source
AND (
    any(cat1 IN p1.categories WHERE any(cat2 IN p2.categories WHERE cat1 = cat2))
    OR
    any(word IN split(toLower(p1.title), ' ') WHERE toLower(p2.title) CONTAINS word AND size(word) > 5)
)
WITH p1, p2 LIMIT 500
MERGE (p1)-[r:RELATED_TOPIC]-(p2)
SET r.reason = 'similar_field'
RETURN count(r) AS related_topic_links
"@

docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 $query4

# Summary
Write-Host "`n📊 Summary of Paper-to-Paper Connections:`n" -ForegroundColor Green

$summary = docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 @"
MATCH (p1:Paper)-[r]->(p2:Paper)
RETURN type(r) AS relationship_type, count(r) AS count
ORDER BY count DESC
"@

$summary

Write-Host "`n✅ Paper-to-paper connections created!`n" -ForegroundColor Green
Write-Host "Refresh the Knowledge Graph tab to see papers connected to each other.`n" -ForegroundColor Cyan
