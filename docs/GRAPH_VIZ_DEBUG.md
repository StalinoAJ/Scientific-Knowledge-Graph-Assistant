# Knowledge Graph Visualization Debug Guide

## Current Issue

When clicking the "Knowledge Graph" tab, you see a blank black screen instead of the graph visualization.

## Diagnostics

### ✅ Backend API is Working
The `/graph/export` endpoint returns data correctly:
- **100 nodes**
- **262 edges**  
- Data format is correct

### 🔍 Added Debugging

I've added console logging to both components:
- `frontend/src/App.tsx` - logs when graph data is loaded
- `frontend/src/visualizations/GraphViz.tsx` - logs when rendering starts

## How to Debug

### 1. Check Browser Console

Open your browser's Developer Tools (F12) and:

1. Go to the **Console** tab
2. Refresh the page (F5)  
3. Click on the "Knowledge Graph" tab
4. Look for these log messages:

```
Loading graph data...
Graph data loaded: {nodes: Array(...), edges: Array(...)}
Nodes: 100 Edges: 262
GraphViz useEffect triggered
Container ref: <div>...</div>
Elements created: 362 elements
```

**If you see errors instead**, take a screenshot and that will tell us exactly what's wrong.

### 2. Restart the Frontend Container

The code changes I made need the frontend to restart:

```powershell
# Method 1: Restart just the frontend
docker-compose restart frontend

# Method 2: Rebuild if needed
docker-compose up -d --build frontend

# Method 3: Full restart
docker-compose down
docker-compose up -d
```

Then:
1. Wait 10-15 seconds for the frontend to compile
2. Open http://localhost:3000 in your browser  
3. Click "Knowledge Graph" tab
4. Check browser console (F12 → Console)

### 3. Check Frontend Container Logs

```powershell
# View frontend build logs
docker logs sci-kg-frontend --tail 50

# If there are compilation errors, you'll see them here
```

## Common Issues & Solutions

### Issue 1: Graph Not Rendering

**Symptoms**: Blank black screen, no console errors

**Cause**: Cytoscape or graph library not loading

**Solution**:
```powershell
# Rebuild frontend with fresh node_modules
docker-compose build frontend
docker-compose up -d frontend
```

### Issue 2: "Cannot read property of undefined"

**Symptoms**: Console shows errors about `data.nodes` or `data.edges`

**Cause**: Data format mismatch

**Solution**: The debugging logs will show exactly what data is being passed. Share the console output.

### Issue 3: Container Crashes

**Symptoms**: Frontend container keeps restarting

**Solution**:
```powershell
# Check logs for error
docker logs sci-kg-frontend

# If syntax error in code, I'll fix it
```

## Quick Test

Run this to verify everything is working:

```powershell
# 1. Restart everything
docker-compose restart

# 2. Wait for services to start
Start-Sleep -Seconds 15

# 3. Test API
Invoke-RestMethod -Uri "http://localhost:8000/graph/export?max_nodes=10"

# 4. Check frontend is running
docker ps | Select-String "frontend"
```

## What Should Work

Once fixed, you should see:

1. **Graph visualization** with colored nodes:
   - 🔵 Blue dots = Papers
   - 🟣 Purple dots = Authors  
   - 🟢 Green dots = Methods
   - 🟠 Orange dots = Datasets

2. **Lines connecting nodes** representing relationships:
   - Papers → Authors (AUTHORED_BY)
   - Papers → Methods (PROPOSES_METHOD)
   - Papers → Datasets (USES_DATASET)

3. **Interactive controls**:
   - Zoom with mouse wheel
   - Drag to pan
   - Click nodes to select
   - Reset view button

## Next Steps

1. **Restart the frontend container**
2. **Open browser console** (F12)
3. **Click Knowledge Graph tab**
4. **Take a screenshot of the console** if there are errors
5. **Share the console output** so I can see exactly what's happening

The debugging logs I added will tell us exactly where the issue is!

---

## TypeScript Lint Errors (Can Ignore)

The IDE is showing many TypeScript errors like:
```
Cannot find module 'react' or its corresponding type declarations
JSX element implicitly has type 'any'
```

**These are HARMLESS** - they're just IDE linting errors because React types aren't fully loaded in the editor. The app will still compile and run fine in the browser. These don't affect runtime behavior.

---

Let me know what you see in the browser console after restarting the frontend! 🔍
