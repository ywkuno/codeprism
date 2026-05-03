# Cortext

Local-first codebase maps, context slices, and visual replay for AI coding agents.

Cortext turns a repository into an inspectable project graph before an assistant reads the whole tree. It maps files, symbols, imports, routes, docs, hierarchy, and activity events, then exports compact context packs that humans and agents can both inspect.

The goal is simple: map first, query next, read raw files only when they matter.

## What It Does

- Builds a local SQLite graph of your repository.
- Extracts deterministic structure from Python, Markdown, and JavaScript/TypeScript files.
- Reuses file hashes so unchanged files are not rescanned.
- Exports Markdown, JSON, DOT, and static browser visualizations.
- Generates stable graph data for visual inspection and tool integration.
- Keeps the visual map readable with multi-column repo-tree layout, cluster-grid fallback, layer toggles, focus mode, and hover tooltips.
- Labels files by semantic role, including agent instructions, repo controls, packages, source, tests, docs, examples, generated files, and dependencies.
- Replays JSONL activity streams over the graph.
- Estimates context size and creates targeted Markdown slices for focused work.

## Status

Cortext is an early MVP, but the core loop is usable:

- MVP1 = mapper and context export.
- MVP2 = visual brain map.
- MVP3 = animated pixel brain / agent replay.
- MVP4 = token stats and targeted context slices.

Token counts are local estimates based on text length. They are useful for comparing full-source, graph, context-pack, and slice sizes, but they are not benchmark claims.

## Install From Source

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Quick Start

```bash
contextopt init
contextopt map .
contextopt export --format md --out .contextopt/context-pack.md
contextopt export --format json --out .contextopt/context-pack.json
contextopt visualize --outdir .contextopt/visual
contextopt stats
contextopt query "Where is authentication handled?"
contextopt slice auth --out .contextopt/slices/auth.md
```

Open `.contextopt/visual/index.html` in a browser to inspect the generated brain map.

## Activity Replay

Cortext can normalize a JSONL event stream and replay touched nodes in the viewer:

```bash
contextopt visualize --activity examples/activity-stream.sample.jsonl --outdir .contextopt/visual
```

Activity rows can reference `node_id`, `from_node_id`, `to_node_id`, or `path`. Malformed rows are skipped and reported as warnings in the generated activity file.

## CLI Commands

| Command | Purpose |
| --- | --- |
| `contextopt init` | Create a local `.contextopt/config.toml` file. |
| `contextopt map .` | Scan the repo and update the SQLite graph. |
| `contextopt export --format md` | Export a Markdown context pack. |
| `contextopt export --format json` | Export stable graph JSON. |
| `contextopt export --format dot` | Export DOT graph data. |
| `contextopt visualize` | Generate a static browser viewer. |
| `contextopt query "topic"` | Rank relevant files and symbols. |
| `contextopt stats` | Estimate source, graph, and pack token sizes. |
| `contextopt slice <target>` | Export a focused Markdown context slice. |

## Token-Saving Workflow

Use Cortext as a preflight step before broad code reading:

```bash
contextopt map .
contextopt stats
contextopt query "billing webhook"
contextopt slice "billing webhook" --out .contextopt/slices/billing-webhook.md
```

That gives an assistant a smaller, inspectable starting point. The assistant should still verify important details in raw source files before editing.

## Privacy Model

- No network calls are made by default.
- Generated artifacts live under `.contextopt/`.
- Outputs are inspectable text, JSON, DOT, HTML, or SQLite.
- Optional LLM summarization is intentionally out of scope for the default path.

## Project Layout

```text
src/contextopt/        Python package and CLI
src/contextopt/exporters/
src/contextopt/extractors/
apps/brain-viz/       Future browser app scaffold
apps/pixel-brain/     Future replay renderer scaffold
docs/                 Architecture, roadmap, and schemas
examples/             Sample project and activity stream
integrations/         Claude, Codex, and Copilot templates
tests/                Regression tests
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
contextopt map .
contextopt export --format json --out .contextopt/context-pack.json
contextopt visualize --activity examples/activity-stream.sample.jsonl --outdir .contextopt/visual
```

## Roadmap

Near-term work is focused on making the visual map more useful, improving slice ranking, and adding deeper static extraction without making the tool heavyweight. See `docs/roadmap.md` for the current plan.

## License

MIT. See `LICENSE`.
