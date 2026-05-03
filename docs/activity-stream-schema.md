# Activity Stream Schema

This schema is meant for future visual overlays and pixel-agent replay.
The log format is newline-delimited JSON (`.jsonl`).

## Base fields

Every event should include:

- `ts` — ISO8601 timestamp
- `run_id` — unique run identifier
- `agent_id` — actor name or agent ID
- `event` — event type string
- `node_id` — optional stable node ID
- `path` — optional repo path
- `meta` — freeform object

## Example event types

### `file_read`
```json
{"ts":"2026-05-03T02:00:00Z","run_id":"demo-1","agent_id":"codex","event":"file_read","node_id":"file::src/app.py::src/app.py","path":"src/app.py","meta":{"reason":"task relevant"}}
```

### `file_write`
```json
{"ts":"2026-05-03T02:01:00Z","run_id":"demo-1","agent_id":"codex","event":"file_write","node_id":"function::src/app.py::main","path":"src/app.py","meta":{"diff_lines":12}}
```

### `context_pack_generated`
```json
{"ts":"2026-05-03T02:02:00Z","run_id":"demo-1","agent_id":"contextopt","event":"context_pack_generated","meta":{"node_count":22,"edge_count":37}}
```

### `test_run`
```json
{"ts":"2026-05-03T02:03:00Z","run_id":"demo-1","agent_id":"codex","event":"test_run","path":"tests/test_app.py","meta":{"status":"passed"}}
```

## Future fields

Potential additions:
- `from_node_id`
- `to_node_id`
- `duration_ms`
- `token_cost`
- `context_pack_id`
- `status`
- `severity`
