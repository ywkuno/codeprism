from __future__ import annotations

import json
from pathlib import Path

from ..graph import GraphStore


def _node_id(row) -> str:
    return f"{row['kind']}::{row['path']}::{row['name']}"


def export_json(store: GraphStore, out: Path) -> None:
    run = store.rows("SELECT * FROM runs ORDER BY id DESC LIMIT 1")
    nodes = store.rows("SELECT * FROM nodes ORDER BY kind, path, name LIMIT 100000")
    edges = store.rows("SELECT * FROM edges ORDER BY kind, source, target LIMIT 200000")

    payload = {
        "meta": {
            "root": run[0]["root"] if run else "",
            "created_at": run[0]["created_at"] if run else "",
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": [
            {
                "id": _node_id(row),
                "kind": row["kind"],
                "path": row["path"],
                "name": row["name"],
                "label": row["name"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "meta": json.loads(row["meta_json"] or "{}"),
            }
            for row in nodes
        ],
        "edges": [
            {
                "source": row["source"],
                "target": row["target"],
                "kind": row["kind"],
                "meta": json.loads(row["meta_json"] or "{}"),
            }
            for row in edges
        ],
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
