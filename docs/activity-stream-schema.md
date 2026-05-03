# Activity Stream Schema

This schema is the MVP2 foundation for future visual overlays and MVP3 pixel-agent replay.
The source log format is newline-delimited JSON (`.jsonl`). `contextopt visualize --activity <file>` normalizes valid rows into `.contextopt/visual/activity-stream.json` and records warnings for malformed rows.

## Base fields

Recommended event fields:

- `ts` — ISO8601 timestamp
- `run_id` — unique run identifier
- `agent_id` — actor name or agent ID
- `event` — event type string
- `node_id` — optional stable node ID
- `from_node_id` — optional stable node ID where a replay movement starts
- `to_node_id` — optional stable node ID where a replay movement ends
- `path` — optional repo path
- `duration_ms` — optional event duration or animation hint
- `status` — optional status such as `ok`, `passed`, `failed`, or `blocked`
- `severity` — optional severity such as `info`, `warn`, or `error`
- `meta` — freeform object

Only `event` is effectively required by the MVP2 parser. Missing optional fields are normalized to empty strings or nulls so replay does not crash.

## Stable node ID examples

- Folder: `folder::src/contextopt`
- File: `file::src/contextopt/cli.py`
- Markdown doc: `doc::docs/visualization-plan.md`
- Function: `function::src/contextopt/cli.py::main`
- Method: `method::src/contextopt/graph.py::commit`
- Class: `class::src/contextopt/graph.py::GraphStore`
- Heading: `heading::README.md::Quick start`
- Route: `route::/users/:id`
- External module: `module::pathlib`

## Example event types

### `file_read`
```json
{"ts":"2026-05-03T02:00:00Z","run_id":"demo-1","agent_id":"codex","event":"file_read","node_id":"file::src/app.py","to_node_id":"file::src/app.py","path":"src/app.py","duration_ms":650,"status":"ok","severity":"info","meta":{"reason":"task relevant"}}
```

### `file_write`
```json
{"ts":"2026-05-03T02:01:00Z","run_id":"demo-1","agent_id":"codex","event":"file_write","from_node_id":"file::src/app.py","to_node_id":"function::src/app.py::main","node_id":"function::src/app.py::main","path":"src/app.py","duration_ms":800,"status":"ok","severity":"info","meta":{"diff_lines":12}}
```

### `context_pack_generated`
```json
{"ts":"2026-05-03T02:02:00Z","run_id":"demo-1","agent_id":"cortext","event":"context_pack_generated","meta":{"node_count":22,"edge_count":37}}
```

### `test_run`
```json
{"ts":"2026-05-03T02:03:00Z","run_id":"demo-1","agent_id":"codex","event":"test_run","path":"tests/test_app.py","meta":{"status":"passed"}}
```

## Future fields

Potential additions:
- `target_path`
- `token_cost`
- `context_pack_id`
- `estimated_tokens`
- `actual_tokens`

## Malformed rows

Malformed JSONL rows are skipped and reported in the generated `activity-stream.json` `warnings` array. Non-object JSON rows are also skipped. The viewer can still load and replay the valid events.
