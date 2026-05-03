from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .exporters.dot import export_dot
from .exporters.json_export import export_json
from .exporters.markdown import export_markdown
from .exporters.web import export_web_visualization
from .graph import GraphStore
from .mapper import map_project
from .query import query_graph


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="contextopt", description="Map a codebase for AI context optimization."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init", help="Create .contextopt config directory.")
    p_init.add_argument("--root", default=".")
    p_map = sub.add_parser("map", help="Scan and map a project.")
    p_map.add_argument("root", nargs="?", default=".")
    p_map.add_argument("--db", default=".contextopt/context.db")
    p_map.add_argument("--max-file-bytes", type=int)
    p_map.add_argument("--ignore", action="append", default=[])
    p_export = sub.add_parser("export", help="Export a context pack.")
    p_export.add_argument("--db", default=".contextopt/context.db")
    p_export.add_argument("--format", choices=["md", "json", "dot"], default="md")
    p_export.add_argument("--out", default=".contextopt/context-pack.md")
    p_export.add_argument("--max-nodes", type=int, default=5000)
    p_export.add_argument("--max-edges", type=int, default=5000)
    p_export.add_argument("--max-chars", type=int)
    p_query = sub.add_parser("query", help="Query the local project map.")
    p_query.add_argument("text")
    p_query.add_argument("--db", default=".contextopt/context.db")
    p_query.add_argument("--limit", type=int, default=20)
    p_visualize = sub.add_parser(
        "visualize",
        help="Generate an interactive browser view of the project map.",
    )
    p_visualize.add_argument("--db", default=".contextopt/context.db")
    p_visualize.add_argument("--outdir", default=".contextopt/visual")
    args = parser.parse_args(argv)
    if args.cmd == "init":
        root = Path(args.root).resolve()
        ctx = root / ".contextopt"
        ctx.mkdir(exist_ok=True)
        config = ctx / "config.toml"
        if not config.exists():
            config.write_text(
                "max_file_bytes = 500000\n"
                'ignore = ["node_modules", ".git", "dist", "build", ".next"]\n',
                encoding="utf-8",
            )
        print(f"Initialized {ctx}")
        return 0
    if args.cmd == "map":
        root = Path(args.root).resolve()
        config = load_config(root)
        db = Path(args.db)
        db.parent.mkdir(parents=True, exist_ok=True)
        result = map_project(
            root,
            GraphStore(db),
            max_file_bytes=args.max_file_bytes or config.max_file_bytes,
            ignore_patterns=[*config.ignore, *args.ignore],
        )
        print(
            f"Mapped {result.files_seen} files, {result.nodes_written} nodes, "
            f"{result.edges_written} edges. Reused {result.files_reused} unchanged, "
            f"extracted {result.files_extracted}, hashed {result.files_hashed}."
        )
        return 0
    if args.cmd == "export":
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        store = GraphStore(Path(args.db))
        if args.format == "dot":
            export_dot(store, out, max_edges=args.max_edges)
        elif args.format == "json":
            export_json(store, out)
        else:
            export_markdown(
                store,
                out,
                max_nodes=args.max_nodes,
                max_edges=args.max_edges,
                max_chars=args.max_chars,
            )
        print(f"Wrote {out}")
        return 0
    if args.cmd == "visualize":
        outdir = Path(args.outdir)
        html_path = export_web_visualization(GraphStore(Path(args.db)), outdir)
        print(f"Wrote visualization to {html_path}")
        return 0
    if args.cmd == "query":
        for row in query_graph(GraphStore(Path(args.db)), args.text, args.limit):
            print(f"{row['kind']:10} {row['path']} {row['name']}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
