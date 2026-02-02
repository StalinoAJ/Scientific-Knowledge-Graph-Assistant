# Admin & Tools Panel (v2) 🛠️

## Overview

A comprehensive administrative dashboard for managing your Scientific Knowledge Graph.

## Features

### 1. System Health Status 🏥
- Real-time check of backend services
- **Neo4j Status**: Indicates if the graph database is online and reachable
- **Ollama Status**: Indicates if the LLM service is ready

### 2. Paper Ingestion Tool 📥
- **Search Topic**: Enter any scientific topic (e.g., "Deep Learning", "CRISPR")
- **Max Papers**: Controls how many papers to fetch (1-50)
- **Feedback**: Shows success/error messages

### 3. Data Management (Danger Zone) 🗑️
> **Warning**: These actions are destructive!

- **Delete specific papers**: Enter a topic or title query. All matching papers (and their exclusive connections) will be deleted.
    *   *Useful for cleaning up irrelevant results from a broad search.*
- **Delete ALL Data**: A prominent red button to wipe the entire database.
    *   *Useful for resetting the project to a clean state.*

## How to Access

1. Refresh your browser (Ctrl+Shift+R)
2. Click the new **"Admin & Tools"** button in the top header (features a modern gradient design)
3. The panel will open as an overlay

## Usage Example: Cleanup

1. Open **Admin & Tools**
2. Scroll to **Data Management**
3. In "Delete Specific Papers", type `biology`
4. Click **Delete Matches**
5. All papers with "biology" in the title/abstract are removed.

## Technical Implementation

- **API**: 
    - `POST /admin/delete`: Handles both full reset and filtered deletion using Cypher queries.
- **Frontend**: 
    - `AdminPanel.tsx`: Updated with deletion logic and confirmation dialogs.
    - `App.css`: Enhanced button styling for a premium feel.
