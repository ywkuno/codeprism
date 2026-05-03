# AGENTS.md

## Project purpose

This repo implements Context Optimizer: a local-first codebase mapping tool that generates compact context packs for AI assistants.

## Ground rules for agents

- Keep code local-first. Do not add network calls unless explicitly requested.
- Prefer deterministic AST/static parsing before LLM summarization.
- Every generated context artifact must be inspectable text or SQLite.
- Avoid viral-project style claims. Use measured language and benchmark honestly.
- Keep the CLI working on Windows, macOS, and Linux.
- Do not introduce heavyweight dependencies unless there is a clear reason.

## Core commands

```bash
pip install -e ".[dev]"
pytest
ruff check .
contextopt map .
contextopt export --format md --out .contextopt/context-pack.md
```

## Architecture

- `src/contextopt/cli.py` — CLI entrypoint
- `src/contextopt/scanner.py` — file discovery and ignore handling
- `src/contextopt/extractors/` — language/document extractors
- `src/contextopt/graph.py` — graph model and SQLite persistence
- `src/contextopt/exporters/` — context pack exporters
- `integrations/` — Claude/Codex/Copilot integration templates
- `docs/` — design, roadmap, agent handoff
