# Context Optimizer

A trustworthy, local-first codebase mapping tool for AI assistants.

Context Optimizer builds a compact, queryable map of a project so AI tools can understand a growing codebase without repeatedly reading every file. Think of it like an IDB map for your repo: symbols, imports, routes, modules, entrypoints, docs, risks, and high-signal summaries.

## Brain map visualization

The repo also includes early scaffolding for a local browser visualization:

- export the project map as inspectable JSON
- generate a static HTML viewer under `.contextopt/visual`
- drag, zoom, filter, and inspect graph nodes
- keep room for a future Pixel Brain Mode driven by JSONL activity events

## Goals

- Save tokens for Claude, Codex, ChatGPT, Copilot, and local agents.
- Keep private code local by default.
- Produce deterministic, inspectable context instead of opaque AI magic.
- Work as a CLI, agent skill, slash command, and repo instruction layer.
- Make context refresh cheap enough to run after every major change.
- Let humans inspect the same project map that agents use.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
contextopt init
contextopt map .
contextopt export --format md --out .contextopt/context-pack.md
contextopt export --format json --out .contextopt/context-pack.json
contextopt visualize --outdir .contextopt/visual
contextopt query "Where is authentication handled?"
```

Open `.contextopt/visual/index.html` in a browser to inspect the static visualization.

## Current implementation

- Python extractor using the standard library AST
- Markdown extractor
- Deterministic JS/TS fallback extractor with Next.js route detection
- Scanner ignore handling with `.gitignore`, size limits, and local config
- Incremental SQLite cache using file hashes
- Markdown, JSON, DOT, and static web visualization exports
- Query ranking for files, symbols, docs, and routes
- Integration stubs for Codex / Claude / Copilot

## Planning docs

- `docs/visualization-plan.md`
- `docs/pixel-brain-mode.md`
- `docs/activity-stream-schema.md`
- `docs/roadmap.md`
