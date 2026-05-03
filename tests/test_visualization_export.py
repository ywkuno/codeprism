from pathlib import Path

from contextopt.exporters.web import export_web_visualization
from contextopt.graph import GraphStore
from contextopt.mapper import map_project


def test_visualization_export(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
    db = tmp_path / "context.db"
    store = GraphStore(db)
    map_project(root, store)
    out_dir = tmp_path / "visual"
    html = export_web_visualization(store, out_dir)
    assert html.exists()
    assert (out_dir / "graph-data.json").exists()
    assert (out_dir / "app.js").exists()
