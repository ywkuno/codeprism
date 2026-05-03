from __future__ import annotations

from .graph import GraphStore


KIND_WEIGHTS = {
    "route": 80,
    "class": 70,
    "function": 65,
    "heading": 45,
    "doc": 35,
    "file": 25,
}


def _score(row: dict, term: str) -> int:
    name = row["name"].lower()
    path = row["path"].lower()
    meta = row.get("meta_json", "").lower()
    score = KIND_WEIGHTS.get(row["kind"], 10)
    if name == term:
        score += 1000
    elif name.startswith(term):
        score += 300
    elif term in name:
        score += 150
    if path == term:
        score += 500
    elif path.endswith(f"/{term}") or path.startswith(term):
        score += 180
    elif term in path:
        score += 90
    if term in meta:
        score += 20
    if row["start_line"] is not None:
        score += 5
    return score


def query_graph(store: GraphStore, text: str, limit: int = 20) -> list[dict]:
    term = text.lower().strip()
    if not term:
        return []
    needle = f"%{term}%"
    rows = store.rows(
        """
        SELECT kind, path, name, start_line, meta_json FROM nodes
        WHERE lower(path) LIKE ? OR lower(name) LIKE ? OR lower(meta_json) LIKE ?
    """,
        (needle, needle, needle),
    )
    ranked = [dict(row) for row in rows]
    for row in ranked:
        row["score"] = _score(row, term)
    return sorted(ranked, key=lambda row: (-row["score"], row["path"], row["name"]))[:limit]
