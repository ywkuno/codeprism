import json
from pathlib import Path

from contextopt.activity import parse_activity_stream
from contextopt.live_trace import append_live_trace_event, live_trace_path


def test_live_trace_path_uses_codeprism_artifact_dir(tmp_path: Path) -> None:
    assert live_trace_path(tmp_path) == tmp_path / ".codeprism" / "live-trace.jsonl"


def test_append_live_trace_event_writes_parseable_activity_jsonl(tmp_path: Path) -> None:
    trace = live_trace_path(tmp_path)

    written = append_live_trace_event(
        trace,
        event="prime",
        path="README.md",
        estimated_tokens=123,
        meta={"query": "quick start"},
    )

    assert written is True
    row = json.loads(trace.read_text(encoding="utf-8"))
    assert row["agent_id"] == "CodePrism"
    assert row["event"] == "prime"
    assert row["path"] == "README.md"
    assert row["node_id"] == "file::README.md"
    assert row["estimated_tokens"] == 123
    assert row["meta"] == {"query": "quick start"}
    events, warnings = parse_activity_stream(trace)
    assert warnings == []
    assert events[0]["event"] == "prime"
