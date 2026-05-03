# Visualization Plan

## Why visualize the map?

Most context-optimization tools stop at “compress repo into machine-readable output”.
That helps the AI, but not the human.

We want a **human-readable codebase brain**:

- understand repo shape at a glance
- spot hotspots, giant files, isolated modules, and dependency tangles
- debug why the AI is reading certain files
- make the mapping feel trustworthy and inspectable

## Core UX goals

### 1. Interactive structure map
- zoom / pan
- drag nodes around
- click nodes to inspect details
- filter by type (file / class / function / doc / route / API / test)
- search by path or symbol name

### 2. Multiple layouts
Phase 1 uses a simple grouped layout.
Future layouts:
- file tree layout
- force graph layout
- dependency DAG
- layered architecture view
- package/module cluster view

### 3. AI context overlay
The real power move:
- show which nodes were included in a context pack
- show which nodes the AI touched during a task
- heatmap the “most-read” or “most-referenced” files

### 4. Human trust layer
Every node should be inspectable:
- source path
- line range
- extracted summary/metadata
- edges to neighbors
- why it was included in context

## Data model additions

Current graph model already supports nodes + edges.
For richer visualization we should add:

- stable node IDs
- parent-child hierarchy edges
- node weight / size metrics
- importance score
- change frequency score
- context hit count
- cluster ID / module ID
- optional file hash

## Recommended implementation phases

### Phase A — current scaffold
- JSON export
- static HTML viewer
- drag / zoom / inspect

### Phase B — better graph intelligence
- explicit tree hierarchy
- dependency clustering
- hotspot sizing
- edge toggles

### Phase C — polished app
Build a real app under `apps/brain-viz`:
- React + TypeScript + Vite
- Cytoscape.js or Sigma.js
- side panels and search
- timeline scrubber
- context inclusion overlays

## Suggested tech choices

### Fastest to MVP
- export JSON from Python CLI
- render with static HTML + vanilla JS or D3

### Better product-grade path
- Python CLI backend
- React frontend
- websocket or file watcher for live refresh

## MVP acceptance criteria

- `contextopt visualize` generates a folder with a browser-openable viewer
- viewer loads local graph JSON
- user can pan, zoom, drag, search, and inspect nodes
- viewer handles at least a few thousand nodes without falling over
