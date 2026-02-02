# Paper-to-Paper Connections - Summary

## Current Status

**❌ No direct paper-to-paper connections exist in your current graph.**

The current relationships are only:
- Papers → Authors (AUTHORED_BY): 118
- Papers → Methods (PROPOSES_METHOD): 96
- Papers → Datasets (USES_DATASET): 48

## Why No Direct Connections?

Your current dataset doesn't have:
1. **Shared authors** - Each paper was written by different authors
2. **Citation data** - The ingestion doesn't capture which papers cite each other
3. **Overlapping methods/datasets** - Papers use different methods/datasets

## How to Add Paper-to-Paper Connections

### Option 1: Ingest More Papers from Same Authors/Groups
```powershell
# Ingest papers from specific research areas that likely share authors
.\ingest_papers.ps1 -Query "AlphaFold protein folding" -MaxResults 20
.\ingest_papers.ps1 -Query "transformer attention mechanism" -MaxResults 20
```

When you have multiple papers by the same research group, `SHARES_AUTHOR` connections will automatically form.

### Option 2: Enable Citation Tracking (Requires Code Enhancement)

Currently, the paper fetchers don't capture citation information. To add this, we would need to:

1. **Extract citations from paper metadata** (available in Semantic Scholar API)
2. **Create CITES relationships** during ingestion
3. **Match cited papers** if they exist in the database

This is a good **future enhancement** but requires modifying the ingestion pipeline.

### Option 3: Semantic Similarity (Requires Embeddings)

Another approach is to use semantic similarity:

1. **Generate embeddings** for paper abstracts
2. **Calculate similarity** between papers
3. **Create SIMILAR_TO edges** for papers with high similarity

This is also a future enhancement.

### Option 4: Manual Connections Based on Topics

You can manually create connections based on the current data:

```powershell
# Connect papers that mention similar keywords in titles
docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 "
MATCH (p1:Paper), (p2:Paper)
WHERE p1.node_id < p2.node_id
AND toLower(p1.title) CONTAINS 'deep learning'
AND toLower(p2.title) CONTAINS 'deep learning'
WITH p1, p2 LIMIT 50
MERGE (p1)-[r:RELATED_TOPIC {topic: 'deep_learning'}]-(p2)
RETURN count(r) AS connections_created
"
```

## Recommended Approach

For now, the **best way to get paper-to-paper connections** is:

1. **Ingest more focused papers** - Papers on the same specific topic
2. **Use narrower queries** - E.g., "ResNet image classification" instead of just "deep learning"
3. **Ingest papers from conferences** - Papers from the same venue often cite each other

Example workflow:
```powershell
# Narrow topic with likely citations
.\ingest_papers.ps1 -Query "BERT language model improvements" -MaxResults 30 -Sources @("semantic_scholar")

# After ingestion, these papers will likely:
# - Share authors
# - Use similar methods (BERT variations)
# - Use similar datasets (GLUE, SQuAD)
```

## Visualization Impact

Once paper-to-paper connections exist, you'll see:
- **Papers clustered by topic** - Related papers grouped together
- **Citation networks** - Papers that build on each other
- **Research lineages** - How ideas evolved over time
- **Collaboration networks** - Papers by same research groups

## Future Enhancements to Add

To make paper-to-paper connections more useful, consider:

1. ✅ **Citation extraction** during ingestion
2. ✅ **Semantic similarity** based on embeddings  
3. ✅ **Co-citation analysis** - Papers cited together are related
4. ✅ **Topic modeling** - Group papers by discovered topics
5. ✅ **Temporal analysis** - Papers from similar time periods

---

## Quick Test

To test if you can create connections, try:

```powershell
# Check if any papers share common words in titles
docker exec sci-kg-neo4j cypher-shell -u neo4j -p scientifickg123 "
MATCH (p1:Paper), (p2:Paper)
WHERE p1.node_id < p2.node_id
RETURN 
    p1.title,
    p2.title,
    [word IN split(toLower(p1.title), ' ') WHERE toLower(p2.title) CONTAINS word AND size(word) > 4] AS shared_words
LIMIT 5
"
```

If you see shared words, you can create `RELATED_TOPIC` connections based on them.

---

**For your current graph, focus on ingesting more related papers to build natural connections!** 📚🔗
