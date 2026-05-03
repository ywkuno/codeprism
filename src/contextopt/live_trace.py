from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import artifact_path

DEFAULT_AGENT_ID = "CodePrism"
DEFAULT_RUN_ID = "codeprism-cli"
TRACE_FILE = "live-trace.jsonl"


def live_trace_path(root: Path, artifact_dir: Path | None = None) -> Path:
    if artifact_dir is not None:
        return artifact_dir / TRACE_FILE
    return artifact_path(root, TRACE_FILE)


def append_live_trace_event(
    trace_path: Path,
    *,
    event: str,
    path: str | None = None,
    node_id: str | None = None,
    from_node_id: str | None = None,
    to_node_id: str | None = None,
    estimated_tokens: int | float | None = None,
    actual_tokens: int | float | None = None,
    duration_ms: int | float | None = None,
    status: str = "ok",
    severity: str = "info",
    run_id: str | None = None,
    agent_id: str = DEFAULT_AGENT_ID,
    meta: dict[str, Any] | None = None,
) -> bool:
    if os.environ.get("CODEPRISM_TRACE", "").lower() in {"0", "false", "off", "no"}:
        return False
    normalized_path = path.replace("\\", "/") if path else None
    payload: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run_id": run_id or os.environ.get("CODEPRISM_RUN_ID") or DEFAULT_RUN_ID,
        "agent_id": agent_id,
        "event": event,
        "status": status,
        "severity": severity,
        "meta": meta or {},
    }
    if normalized_path:
        payload["path"] = normalized_path
    if node_id or normalized_path:
        payload["node_id"] = node_id or f"file::{normalized_path}"
    if from_node_id:
        payload["from_node_id"] = from_node_id
    if to_node_id:
        payload["to_node_id"] = to_node_id
    if isinstance(estimated_tokens, int | float):
        payload["estimated_tokens"] = estimated_tokens
    if isinstance(actual_tokens, int | float):
        payload["actual_tokens"] = actual_tokens
    if isinstance(duration_ms, int | float):
        payload["duration_ms"] = duration_ms
    try:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with trace_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError:
        return False
    return True
