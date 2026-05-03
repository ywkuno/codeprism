from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph import GraphStore
from .ids import stable_node_id
from .query import query_graph
from .token_estimator import estimate_tokens


def _node_row_id(row: dict[str, Any]) -> str:
    return stable_node_id(row["kind"], row["path"], row["name"])


def _latest_run_filter(store: GraphStore) -> tuple[str, tuple[object, ...]]:
    run = store.rows("SELECT id FROM runs ORDER BY id DESC LIMIT 1")
    if not run:
        return "", ()
    return "WHERE run_id = ?", (run[0]["id"],)


def _nodes_by_id(store: GraphStore) -> dict[str, dict[str, Any]]:
    where, params = _latest_run_filter(store)
    rows = store.rows(f"SELECT * FROM nodes {where}", params)
    return {_node_row_id(dict(row)): dict(row) for row in rows}


def _edge_rows(store: GraphStore) -> list[dict[str, Any]]:
    where, params = _latest_run_filter(store)
    return [dict(row) for row in store.rows(f"SELECT * FROM edges {where}", params)]


def _legacy_tokens_for_node(node: dict[str, Any]) -> set[str]:
    tokens = {_node_row_id(node)}
    if node["kind"] in {"file", "doc"}:
        tokens.add(f"file:{node['path']}")
    tokens.add(f"py:{node['path']}:{node['name']}")
    tokens.add(f"js:{node['path']}:{node['name']}")
    if node["kind"] == "heading":
        tokens.add(f"heading:{node['path']}:{node['name']}")
    if node["kind"] == "route":
        tokens.add(f"route:{node['name']}")
    return tokens


def _resolve_edges(
    edges: list[dict[str, Any]],
    nodes_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    lookup: dict[str, str] = {}
    for node_id, node in nodes_by_id.items():
        for token in _legacy_tokens_for_node(node):
            lookup[token] = node_id
    resolved: list[dict[str, Any]] = []
    for edge in edges:
        source = lookup.get(edge["source"], edge["source"])
        target = lookup.get(edge["target"], edge["target"])
        resolved.append({**edge, "source": source, "target": target})
    return resolved


def _sanitize_filename(text: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in text.strip()]
    slug = "-".join(part for part in "".join(chars).split("-") if part)
    return slug or "slice"


def default_slice_path(query: str) -> Path:
    return Path(".contextopt") / "slices" / f"{_sanitize_filename(query)}.md"


def export_slice(
    store: GraphStore,
    query: str,
    out: Path,
    *,
    limit: int = 12,
) -> dict[str, Any]:
    matches = query_graph(store, query, limit)
    nodes_by_id = _nodes_by_id(store)
    edges = _resolve_edges(_edge_rows(store), nodes_by_id)
    selected_ids = {_node_row_id(match) for match in matches}
    matched_ids = set(selected_ids)

    for edge in edges:
        if edge["source"] in matched_ids:
            selected_ids.add(edge["target"])
        if edge["target"] in matched_ids:
            selected_ids.add(edge["source"])

    selected_nodes = [
        nodes_by_id[node_id] for node_id in sorted(selected_ids) if node_id in nodes_by_id
    ]
    selected_edges = [
        edge
        for edge in edges
        if edge["source"] in selected_ids or edge["target"] in selected_ids
    ]

    lines = [
        "# Cortext Slice",
        "",
        f"- Query: `{query}`",
        f"- Matched nodes: {len(matched_ids)}",
        f"- Written nodes: {len(selected_nodes)}",
        f"- Direct edges: {len(selected_edges)}",
        "",
        "## Nodes",
        "",
    ]
    for node in selected_nodes:
        node_id = _node_row_id(node)
        loc = f":L{node['start_line']}" if node["start_line"] else ""
        lines.append(f"- `{node_id}` — {node['kind']} `{node['path']}{loc}` **{node['name']}**")

    lines += ["", "## Direct Edges", ""]
    for edge in selected_edges:
        lines.append(f"- `{edge['source']}` --{edge['kind']}--> `{edge['target']}`")

    text = "\n".join(lines) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return {
        "query": query,
        "matched_nodes": len(matched_ids),
        "written_nodes": len(selected_nodes),
        "direct_edges": len(selected_edges),
        "estimated_tokens": estimate_tokens(text),
        "out": str(out),
    }
