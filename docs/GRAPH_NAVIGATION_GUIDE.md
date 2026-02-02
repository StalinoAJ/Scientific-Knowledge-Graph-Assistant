# Enhanced Graph Navigation - User Guide 🎨

## Overview

The knowledge graph visualization has been completely redesigned to be much more user-friendly and easier to navigate!

![Enhanced Graph View](docs/enhanced-graph.png)

---

## New Features

### 🔍 **Search Functionality**
- **Location**: Top-left search box
- **What it does**: Instantly filters nodes as you type
- **Searches**: Node titles, names, and IDs
- **How to use**: 
  1. Click the search box
  2. Type keywords (e.g., "deep learning", "protein", author name)
  3. Graph updates in real-time to show only matching nodes

### 🎛️ **Node Type Filters**
- **Location**: Below search box
- **What it does**: Show/hide specific types of nodes
- **Node types**:
  - 🔵 **Papers** - Research papers
  - 🟣 **Authors** - Paper authors
  - 🟢 **Methods** - Algorithms and techniques
  - 🟠 **Datasets** - Training and evaluation datasets
- **How to use**: Click checkboxes to toggle node types on/off
- **Shows**: Count of each node type

### 📐 **Layout Options**
- **Location**: Bottom of filter panel
- **Layouts available**:
  - **Force** - Physics-based layout (default, best for seeing relationships)
  - **Circle** - Nodes arranged in a circle
  - **Grid** - Nodes in a grid pattern
- **How to use**: Click layout buttons to switch between layouts
- **Tip**: Use "Force" for exploring connections, "Grid" for browsing all nodes

### 🔎 **Zoom Controls**
- **Location**: Top-right corner
- **Controls**:
  - **🔍+** Zoom In
  - **🔍-** Zoom Out
  - **⟲** Reset View - Fits all nodes in view
  - **↻** Re-layout - Rearranges nodes with current layout
- **Alternative**: 
  - Mouse wheel to zoom
  - Click and drag to pan

### 💡 **Node Tooltips**
- **How to activate**: Hover mouse over any node
- **Shows**: Node type and full name/title
- **Auto-hides** when you move cursor away

### 🎯 **Node Selection & Highlighting**
- **Click any node** to:
  - Highlight the node
  - Highlight all connected nodes
  - Highlight all connecting edges
  - Show edge labels
- **Click background** to clear selection

### 📊 **Stats Panel**
- **Location**: Bottom-left corner
- **Shows**:
  - Total visible nodes (updates with filters)
  - Total edges in graph
- **Updates**: Real-time as you filter

---

## How to Navigate Effectively

### For Exploring Connections
1. ✅ Use **Force layout** (default)
2. ✅ **Click a paper** to see its authors, methods, and datasets
3. ✅ **Zoom in** to see details
4. ✅ **Zoom out** to see overall structure

### For Finding Specific Papers
1. ✅ Type in **search box** (e.g., "transformer")
2. ✅ Filter visible **node types** if needed
3. ✅ **Click matching nodes** to explore connections

### For Browsing by Category
1. ✅ Uncheck all node types **except one** (e.g., only Papers)
2. ✅ Switch to **Grid layout** for easier viewing
3. ✅ **Zoom** to see all at once

### For Understanding Author Collaborations
1. ✅ Filter to show only **Papers and Authors**
2. ✅ **Search for an author** name
3. ✅ **Click the author node** to see all their papers

### For Method/Dataset Usage
1. ✅ Filter to show **Papers, Methods, and Datasets**
2. ✅ **Search for a method** (e.g., "BERT", "ResNet")
3. ✅ **Click the method node** to see which papers use it

---

## Tips & Tricks

### 🚀 Performance Tips
- **Hide node types** you don't need to reduce clutter
- **Search first** before exploring to find relevant areas
- **Use Reset View** if you get lost
- **Switch layouts** if one doesn't work well for your data

### 🎨 Visual Clarity
- **Nodes are color-coded** by type:
  - Blue = Papers
  - Purple = Authors
  - Green = Methods
  - Orange = Datasets
- **Thicker lines** = Highlighted edges
- **Larger nodes** = Selected/highlighted nodes
- **White outline** = Selected node

### 🔍 Finding Hidden Nodes
- If a node seems missing:
  1. Check if its **type is filtered out**
  2. Clear the **search box**
  3. Click **Reset View**

### 📱 Mobile/Small Screens
- Filter panel auto-hides on small screens
- Use zoom controls for navigation
- Search box always visible

---

## Keyboard Shortcuts

While we don't have keyboard shortcuts yet, here are mouse tricks:

| Action | How To |
|--------|--------|
| **Pan** | Click and drag background |
| **Zoom** | Mouse wheel up/down |
| **Select** | Click node |
| **Deselect** | Click background |

---

## Troubleshooting

### Graph shows no nodes
- ✅ Check if all node types are unchecked
- ✅ Clear search box
- ✅ Click "Reset View"

### Graph is too cluttered
- ✅ Use search to filter
- ✅ Uncheck some node types
- ✅ Try Circle or Grid layout

### Can't see node labels
- ✅ Zoom in closer
- ✅ Hover to see tooltip
- ✅ Click node to highlight and see full name

### Graph won't update
- ✅ Hard refresh browser (Ctrl+Shift+R)
- ✅ Check browser console for errors

---

## Example Workflows

### Research a Topic
1. Search for topic keyword
2. Click a relevant paper
3. See connected authors and methods
4. Click method nodes to find other papers using it

### Find Collaborators
1. Search for author name
2. Click author node
3. See all papers they authored
4. See co-authors through shared papers

### Explore Datasets
1. Filter to show Only Datasets and Papers
2. Click a dataset node
3. See which papers use it
4. Identify popular datasets

### Compare Methods
1. Search for first method
2. Note papers using it
3. Clear search, search second method
4. Compare paper overlap

---

## Future Enhancements (Coming Soon)

- 🔜 Keyboard shortcuts
- 🔜 Export graph as image
- 🔜 Save/load custom layouts
- 🔜 Node clustering for large graphs
- 🔜 Time-based filtering
- 🔜 Full-text search in abstracts
- 🔜 Minimap navigation

---

## Comparison: Before vs After

### Before ❌
- No search
- No filters
- Fixed layout
- No zoom controls
- No tooltips
- Hard to navigate
- Couldn't hide nodes

### After ✅
- Real-time search
- Type filters with counts
- 3 layout options
- Full zoom/pan controls
- Hover tooltips
- Click to highlight
- Show/hide any type
- Stats panel
- Much cleaner UI

---

**Enjoy exploring your knowledge graph!** 🚀📊✨

For issues or suggestions, check the console logs or documentation.
