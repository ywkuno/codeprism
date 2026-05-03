from __future__ import annotations

from pathlib import Path

from .json_export import export_json
from ..graph import GraphStore

HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>ContextOpt Brain Map</title>
  <link rel=\"stylesheet\" href=\"styles.css\" />
</head>
<body>
  <aside class=\"sidebar\">
    <h1>🧠 Context Brain</h1>
    <p class=\"muted\">Visual map of your codebase for AI context optimization.</p>
    <div class=\"panel\">
      <label>Search</label>
      <input id=\"search\" placeholder=\"file, class, function...\" />
      <label>Filter kind</label>
      <select id=\"kindFilter\">
        <option value=\"all\">All</option>
      </select>
      <div class=\"button-row\">
        <button id=\"layoutBtn\">Re-layout</button>
        <button id=\"fitBtn\">Fit</button>
      </div>
    </div>
    <div class=\"panel\">
      <h2>Legend</h2>
      <ul id=\"legend\"></ul>
    </div>
    <div class=\"panel\">
      <h2>Selected</h2>
      <pre id=\"details\">Click a node to inspect it.</pre>
    </div>
    <div class=\"panel\">
      <h2>Stats</h2>
      <div id=\"stats\"></div>
    </div>
    <div class=\"panel\">
      <h2>Pixel Brain Mode (planned)</h2>
      <p class=\"muted\">Future overlay: agent sprites walk the map using JSONL activity events.</p>
    </div>
  </aside>
  <main>
    <svg id=\"graph\" viewBox=\"0 0 1600 1000\" aria-label=\"Interactive project map\">
      <g id=\"viewport\">
        <g id=\"edges\"></g>
        <g id=\"nodes\"></g>
        <g id=\"labels\"></g>
      </g>
    </svg>
  </main>
  <script src=\"app.js\"></script>
</body>
</html>
"""

CSS = """
:root {
  --bg: #08111f;
  --panel: #0f1b2d;
  --panel2: #13233b;
  --text: #e8eef9;
  --muted: #9fb0cf;
  --border: #223757;
  --accent: #66c8ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  display: grid;
  grid-template-columns: 340px 1fr;
  height: 100vh;
}
.sidebar {
  padding: 16px;
  overflow: auto;
  border-right: 1px solid var(--border);
  background: linear-gradient(180deg, #0a1629 0%, #08111f 100%);
}
main { height: 100vh; }
#graph { width: 100%; height: 100%; display: block; background: radial-gradient(circle at center, rgba(32,65,106,0.35), rgba(8,17,31,1)); }
h1, h2 { margin: 0 0 8px; }
h1 { font-size: 1.35rem; }
h2 { font-size: 1rem; }
.panel {
  background: rgba(15, 27, 45, 0.9);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  margin: 12px 0;
}
label { display: block; margin: 8px 0 4px; font-size: 0.9rem; color: var(--muted); }
input, select, button {
  width: 100%;
  background: var(--panel2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
}
.button-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
button { cursor: pointer; }
button:hover { border-color: var(--accent); }
.muted { color: var(--muted); }
pre { white-space: pre-wrap; font-size: 0.82rem; margin: 0; color: var(--text); }
#legend { list-style: none; padding: 0; margin: 0; }
#legend li { display: flex; align-items: center; gap: 8px; margin: 4px 0; color: var(--muted); }
.swatch { width: 12px; height: 12px; border-radius: 999px; display: inline-block; }
.node { cursor: grab; }
.node circle { stroke: rgba(255,255,255,0.25); stroke-width: 1; }
.node.selected circle { stroke: white; stroke-width: 2; }
.label { font-size: 12px; fill: rgba(255,255,255,0.9); pointer-events: none; }
.edge { stroke: rgba(145,175,222,0.25); stroke-width: 1.2; }
.edge.highlight { stroke: rgba(255,255,255,0.85); stroke-width: 2; }
"""

JS = r"""
const COLORS = {
  file: '#67e8f9',
  module: '#f59e0b',
  class: '#a78bfa',
  function: '#34d399',
  method: '#22c55e',
  heading: '#f472b6',
  doc: '#60a5fa',
  unknown: '#94a3b8'
};

const state = {
  data: null,
  nodes: [],
  edges: [],
  hiddenKinds: new Set(),
  selectedId: null,
  scale: 1,
  tx: 0,
  ty: 0,
  dragNode: null,
  pan: null,
};

const svg = document.getElementById('graph');
const viewport = document.getElementById('viewport');
const nodeLayer = document.getElementById('nodes');
const edgeLayer = document.getElementById('edges');
const labelLayer = document.getElementById('labels');
const details = document.getElementById('details');
const stats = document.getElementById('stats');
const legend = document.getElementById('legend');
const searchInput = document.getElementById('search');
const kindFilter = document.getElementById('kindFilter');

document.getElementById('layoutBtn').addEventListener('click', () => {
  if (!state.data) return;
  buildScene(state.data);
});

document.getElementById('fitBtn').addEventListener('click', fitView);
searchInput.addEventListener('input', applyFilters);
kindFilter.addEventListener('change', applyFilters);

svg.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.92 : 1.08;
  state.scale = Math.max(0.2, Math.min(4, state.scale * factor));
  renderTransform();
}, { passive: false });

svg.addEventListener('mousedown', (e) => {
  if (e.target === svg) {
    state.pan = { x: e.clientX, y: e.clientY, tx: state.tx, ty: state.ty };
  }
});
window.addEventListener('mousemove', (e) => {
  if (state.dragNode) {
    const pt = clientToWorld(e.clientX, e.clientY);
    state.dragNode.x = pt.x;
    state.dragNode.y = pt.y;
    renderGraph();
  } else if (state.pan) {
    state.tx = state.pan.tx + (e.clientX - state.pan.x);
    state.ty = state.pan.ty + (e.clientY - state.pan.y);
    renderTransform();
  }
});
window.addEventListener('mouseup', () => {
  state.dragNode = null;
  state.pan = null;
});

function clientToWorld(clientX, clientY) {
  const rect = svg.getBoundingClientRect();
  const x = (clientX - rect.left - state.tx) / state.scale;
  const y = (clientY - rect.top - state.ty) / state.scale;
  return { x, y };
}

function renderTransform() {
  viewport.setAttribute('transform', `translate(${state.tx}, ${state.ty}) scale(${state.scale})`);
}

function buildTreeBuckets(nodes) {
  const buckets = new Map();
  for (const node of nodes) {
    const filePath = node.path || 'unknown';
    const fileKey = `file:${filePath}`;
    if (!buckets.has(fileKey)) buckets.set(fileKey, []);
    buckets.get(fileKey).push(node);
  }
  return [...buckets.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

function applyInitialLayout(nodes) {
  const buckets = buildTreeBuckets(nodes);
  const columnGap = 260;
  const rowGap = 180;
  let fileIndex = 0;

  for (const [_, group] of buckets) {
    const col = fileIndex % 5;
    const row = Math.floor(fileIndex / 5);
    const baseX = 180 + col * columnGap;
    const baseY = 140 + row * rowGap;
    const fileNode = group.find(n => n.kind === 'file') || group[0];
    fileNode.x = baseX;
    fileNode.y = baseY;

    let angle = 0;
    const childNodes = group.filter(n => n !== fileNode);
    const radius = 72 + Math.min(childNodes.length, 12) * 5;
    for (const child of childNodes) {
      child.x = baseX + Math.cos(angle) * radius;
      child.y = baseY + Math.sin(angle) * radius;
      angle += (Math.PI * 2) / Math.max(1, childNodes.length);
    }
    fileIndex += 1;
  }
}

function buildScene(data) {
  const nodes = data.nodes.map(node => ({ ...node, visible: true }));
  const idLookup = new Map(nodes.map(n => [n.id, n]));
  const fileIdByPath = new Map();
  for (const node of nodes) {
    if (node.kind === 'file') fileIdByPath.set(node.path, node.id);
  }

  const edges = [];
  for (const edge of data.edges) {
    let sourceId = edge.source;
    let targetId = edge.target;

    if (!idLookup.has(sourceId) && edge.source.startsWith('file:')) {
      sourceId = edge.source.replace(/^file:/, 'file::') + '::' + edge.source.replace(/^file:/, '');
    }

    if (!idLookup.has(targetId) && fileIdByPath.has(edge.target)) {
      targetId = fileIdByPath.get(edge.target);
    }

    if (!idLookup.has(sourceId)) {
      const sourceNode = nodes.find(n => n.name === edge.source || n.path === edge.source);
      if (sourceNode) sourceId = sourceNode.id;
    }
    if (!idLookup.has(targetId)) {
      const targetNode = nodes.find(n => n.name === edge.target || n.path === edge.target);
      if (targetNode) targetId = targetNode.id;
    }

    if (idLookup.has(sourceId) && idLookup.has(targetId)) {
      edges.push({ ...edge, sourceId, targetId });
    }
  }

  state.data = data;
  state.nodes = nodes;
  state.edges = edges;
  applyInitialLayout(nodes);
  populateFilters(nodes);
  populateLegend(nodes);
  renderStats(data, nodes, edges);
  fitView();
  renderGraph();
}

function populateFilters(nodes) {
  const kinds = [...new Set(nodes.map(n => n.kind))].sort();
  kindFilter.innerHTML = '<option value="all">All</option>' + kinds.map(k => `<option value="${k}">${k}</option>`).join('');
}

function populateLegend(nodes) {
  const kinds = [...new Set(nodes.map(n => n.kind))].sort();
  legend.innerHTML = kinds.map(kind => `<li><span class="swatch" style="background:${COLORS[kind] || COLORS.unknown}"></span>${kind}</li>`).join('');
}

function renderStats(data, nodes, edges) {
  const fileCount = nodes.filter(n => n.kind === 'file').length;
  stats.innerHTML = `
    <div>Root: <strong>${data.meta.root || '-'}</strong></div>
    <div>Created: <strong>${data.meta.created_at || '-'}</strong></div>
    <div>Files: <strong>${fileCount}</strong></div>
    <div>Nodes: <strong>${nodes.length}</strong></div>
    <div>Edges: <strong>${edges.length}</strong></div>
  `;
}

function fitView() {
  state.scale = 1;
  state.tx = 20;
  state.ty = 20;
  renderTransform();
}

function applyFilters() {
  const text = searchInput.value.trim().toLowerCase();
  const selectedKind = kindFilter.value;
  for (const node of state.nodes) {
    const matchesText = !text || node.name.toLowerCase().includes(text) || node.path.toLowerCase().includes(text);
    const matchesKind = selectedKind === 'all' || node.kind === selectedKind;
    node.visible = matchesText && matchesKind;
  }
  renderGraph();
}

function renderGraph() {
  const visibleIds = new Set(state.nodes.filter(n => n.visible).map(n => n.id));
  edgeLayer.innerHTML = '';
  nodeLayer.innerHTML = '';
  labelLayer.innerHTML = '';

  for (const edge of state.edges) {
    if (!visibleIds.has(edge.sourceId) || !visibleIds.has(edge.targetId)) continue;
    const source = state.nodes.find(n => n.id === edge.sourceId);
    const target = state.nodes.find(n => n.id === edge.targetId);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', source.x);
    line.setAttribute('y1', source.y);
    line.setAttribute('x2', target.x);
    line.setAttribute('y2', target.y);
    line.setAttribute('class', 'edge' + (state.selectedId && (edge.sourceId === state.selectedId || edge.targetId === state.selectedId) ? ' highlight' : ''));
    edgeLayer.appendChild(line);
  }

  for (const node of state.nodes) {
    if (!node.visible) continue;
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'node' + (state.selectedId === node.id ? ' selected' : ''));
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('r', node.kind === 'file' ? 16 : 11);
    circle.setAttribute('fill', COLORS[node.kind] || COLORS.unknown);
    g.appendChild(circle);
    g.addEventListener('mousedown', (e) => {
      e.stopPropagation();
      state.dragNode = node;
      state.selectedId = node.id;
      showDetails(node);
      renderGraph();
    });
    g.addEventListener('click', (e) => {
      e.stopPropagation();
      state.selectedId = node.id;
      showDetails(node);
      renderGraph();
    });
    nodeLayer.appendChild(g);

    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', node.x + 16);
    label.setAttribute('y', node.y + 4);
    label.setAttribute('class', 'label');
    label.textContent = node.name;
    labelLayer.appendChild(label);
  }
}

function showDetails(node) {
  const neighbors = state.edges
    .filter(edge => edge.sourceId === node.id || edge.targetId === node.id)
    .map(edge => `${edge.kind}: ${edge.sourceId === node.id ? edge.targetId : edge.sourceId}`)
    .slice(0, 25);
  details.textContent = JSON.stringify({
    id: node.id,
    kind: node.kind,
    path: node.path,
    name: node.name,
    start_line: node.start_line,
    end_line: node.end_line,
    meta: node.meta,
    neighbors,
  }, null, 2);
}

fetch('graph-data.json')
  .then(r => r.json())
  .then(data => buildScene(data))
  .catch(err => {
    details.textContent = 'Failed to load graph-data.json\n\n' + String(err);
  });
"""


def export_web_visualization(store: GraphStore, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    export_json(store, out_dir / "graph-data.json")
    (out_dir / "index.html").write_text(HTML, encoding="utf-8")
    (out_dir / "styles.css").write_text(CSS, encoding="utf-8")
    (out_dir / "app.js").write_text(JS, encoding="utf-8")
    return out_dir / "index.html"
