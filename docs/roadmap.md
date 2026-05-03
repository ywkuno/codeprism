# Cortext Roadmap

## Milestone names

- MVP1 = mapper and context export.
- MVP2 = visual brain map.
- MVP3 = animated pixel brain / agent replay.
- MVP4 = token optimization and targeted context slices.

## Phase 0 — Starter scaffold

- CLI skeleton
- Scanner
- SQLite graph
- Python extractor
- Markdown exporter
- Claude/Codex/Copilot integration templates

## MVP1 — Mapper and Context Export

- Robust ignore handling
- Incremental cache using file hashes
- Better JS/TS parsing
- Next.js route detector
- Import graph visualization export
- `contextopt query` ranking improvements
- Context pack size budgets

## MVP2 — Visual Brain Map

- JSON export
- Stable graph JSON schema
- Stable node IDs across repeated map runs
- Parent-child hierarchy edges
- Generated static HTML viewer
- Pan / zoom / drag / search / filter / inspect
- Selected-node direct-neighbor highlighting
- Incoming and outgoing edge lists in the selected-node panel
- Optional JSONL activity stream normalization and basic replay
- File-clustered tree-like layout
- Browser app scaffold in `apps/brain-viz`

## MVP2.5 — Visual Clarity Pass

- Default clean overview that hides external modules, imports, and symbol-level detail.
- Layer toggles for structure, symbols, imports, external modules, tests, activity, and labels.
- Focus mode for inspecting the selected node plus its direct neighborhood.
- Hover tooltips for quick node inspection.
- Label-density rules so large maps do not turn into text soup.
- Real fit-to-visible-map behavior.

## MVP2.6 — Repo Tree Layout

- Repo tree is the default visual layout, matching the folder hierarchy users expect.
- The repo tree splits top-level folders into multiple columns so large projects do not become one tall spine.
- Cluster grid remains available as an alternate layout mode.
- Structure stays the base map; imports, symbols, tests, and modules remain optional overlays.
- Activity replay rides on top of either layout.

## MVP2.7 — Semantic Roles / Repo Legend

- Nodes keep their technical `kind`, and also get a semantic `meta.role`.
- Roles include agent instructions, repo controls, packages, source, tests, docs, examples, generated/cache, dependencies, and project files.
- Viewer role filter and role legend make special files easier to spot.
- Role colors and badges distinguish AI-facing docs, Git/repo policy, package files, and dependencies without using red for normal control files.
- Generated/ignored/dependency-heavy areas should stay collapsed or hidden by default; future work can add cheap ghost nodes with counts.

## MVP3 — Animated Pixel Brain / Agent Replay

- Richer JSONL activity stream
- Event replay timeline, event list, speed control, and reset
- Moving agent markers over known graph nodes
- Deterministic path interpolation between touched nodes
- Task timeline and playback controls
- Context inclusion overlays
- Pixel renderer scaffold in `apps/pixel-brain`

## MVP4 — Token Optimization

- `contextopt stats` for source, graph, and context-pack token estimates
- `contextopt slice <path-or-symbol>` for targeted Markdown context packs
- Query-first workflow docs for Codex/Claude usage
- Honest estimated token reporting rather than benchmark claims
- Future: rank slices by imports, call graph, changed files, and docs mentions

## Phase 5 — Agent integrations

- Claude Skill packaging script
- Claude Code slash commands
- Codex workflow prompts
- Copilot instruction templates
- VS Code task definitions
- `contextopt install-integrations`

## Phase 6 — Advanced graph intelligence

- Tree-sitter support
- Call graph for supported languages
- Symbol rename tracking
- Git diff-aware context updates
- Risk hotspots: huge files, circular deps, stale docs
- Optional local LLM summaries via Ollama

## Phase 7 — Project OS integration

- Agent task queue
- Context snapshots per issue
- before/after graph diff for PRs
- CI job that checks context pack freshness
- Web UI or Tauri desktop app
