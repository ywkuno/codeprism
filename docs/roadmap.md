# Roadmap

## Phase 0 — Starter scaffold

- CLI skeleton
- Scanner
- SQLite graph
- Python extractor
- Markdown exporter
- Claude/Codex/Copilot integration templates

## Phase 1 — Useful local MVP

- Robust ignore handling
- Incremental cache using file hashes
- Better JS/TS parsing
- Next.js route detector
- Import graph visualization export
- `contextopt query` ranking improvements
- Context pack size budgets

## Phase 2 — Brain map visualization

- JSON export
- Generated static HTML viewer
- Pan / zoom / drag / search / inspect
- File-clustered tree-like layout
- Browser app scaffold in `apps/brain-viz`
- Pixel renderer scaffold in `apps/pixel-brain`

## Phase 3 — Agent integrations

- Claude Skill packaging script
- Claude Code slash commands
- Codex workflow prompts
- Copilot instruction templates
- VS Code task definitions
- `contextopt install-integrations`

## Phase 4 — Advanced graph intelligence

- Tree-sitter support
- Call graph for supported languages
- Symbol rename tracking
- Git diff-aware context updates
- Risk hotspots: huge files, circular deps, stale docs
- Optional local LLM summaries via Ollama

## Phase 5 — Pixel Brain mode

- JSONL activity stream
- Event replay
- Moving agent markers or sprites
- Task timeline and playback controls
- Context inclusion overlays

## Phase 6 — Project OS integration

- Agent task queue
- Context snapshots per issue
- before/after graph diff for PRs
- CI job that checks context pack freshness
- Web UI or Tauri desktop app
