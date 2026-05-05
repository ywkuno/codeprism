from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


DEFAULT_CONFIG = "examples/field-notes/public-repos.json"
DEFAULT_OUTDIR = ".codeprism/field-notes"
DEFAULT_REPOS_ROOT = "external"


class FieldNoteError(Exception):
    """Raised when field-note inputs cannot be prepared."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run CodePrism field-note measurements against local public repo checkouts."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--repos-root", default=DEFAULT_REPOS_ROOT)
    parser.add_argument("--target", action="append", default=[], help="Target slug or name to run.")
    parser.add_argument("--root", help="Run a single local repo instead of loading --config.")
    parser.add_argument("--name", help="Name for --root single-target mode.")
    parser.add_argument("--slug", help="Slug for --root single-target mode.")
    parser.add_argument("--url", default="", help="Public source URL for --root single-target mode.")
    parser.add_argument("--query", default="main", help="Query for --root single-target mode.")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--max-tokens", type=int, default=8000)
    parser.add_argument("--fail-on-missing", action="store_true")
    parser.add_argument(
        "--codeprism-command",
        help="Command used to invoke CodePrism. Defaults to this Python running contextopt.cli.",
    )
    args = parser.parse_args(argv)

    root = Path.cwd()
    outdir = _resolve_path(args.outdir, root)
    repos_root = _resolve_path(args.repos_root, root)
    codeprism = _command_parts(args.codeprism_command, [sys.executable, "-m", "contextopt.cli"])

    try:
        targets = _targets_from_args(args, root)
    except FieldNoteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    outdir.mkdir(parents=True, exist_ok=True)
    results = [
        _run_target(
            target,
            outdir=outdir,
            repos_root=repos_root,
            codeprism=codeprism,
            limit=args.limit,
            max_tokens=args.max_tokens,
        )
        for target in targets
    ]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    summary = {
        "schema_version": 1,
        "generated_at": generated_at,
        "config": str(_resolve_path(args.config, root)) if not args.root else None,
        "repos_root": str(repos_root),
        "note": (
            "Field notes are local, reproducible measurements for public repo checkouts. "
            "They are not release fixture guarantees."
        ),
        "results": results,
        "summary": _summarize(results),
    }
    summary_json = outdir / "summary.json"
    summary_md = outdir / "summary.md"
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_md.write_text(_format_summary_markdown(summary), encoding="utf-8")

    print(f"Wrote field-note summary {summary_md}")
    failures = [result for result in results if result["status"] == "failed"]
    missing = [result for result in results if result["status"] == "missing"]
    if failures or (missing and args.fail_on_missing):
        print(
            "Field-note run incomplete: "
            f"{len(failures)} failed, {len(missing)} missing.",
            file=sys.stderr,
        )
        return 1
    print(
        "Field-note run complete: "
        f"{summary['summary']['passed']} passed, "
        f"{summary['summary']['missing']} missing, "
        f"{summary['summary']['failed']} failed."
    )
    return 0


def _targets_from_args(args: argparse.Namespace, cwd: Path) -> list[dict[str, Any]]:
    if args.root:
        name = args.name or Path(args.root).name
        return [
            {
                "name": name,
                "slug": args.slug or _slug(name),
                "url": args.url,
                "query": args.query,
                "root": args.root,
            }
        ]

    config_path = _resolve_path(args.config, cwd)
    if not config_path.exists():
        raise FieldNoteError(f"field-note config not found: {config_path}")
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FieldNoteError(f"invalid field-note config {config_path}: {exc}") from exc
    raw_targets = payload.get("targets")
    if not isinstance(raw_targets, list):
        raise FieldNoteError("field-note config must contain a targets array")

    targets = [_normalize_target(target) for target in raw_targets]
    selected = {value.lower() for value in args.target}
    if selected:
        targets = [
            target
            for target in targets
            if target["slug"].lower() in selected or target["name"].lower() in selected
        ]
    if not targets:
        raise FieldNoteError("no field-note targets selected")
    return targets


def _normalize_target(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FieldNoteError("field-note target entries must be objects")
    name = str(value.get("name") or "").strip()
    if not name:
        raise FieldNoteError("field-note targets require a name")
    slug = str(value.get("slug") or _slug(name))
    return {
        "name": name,
        "slug": _slug(slug),
        "url": str(value.get("url") or ""),
        "query": str(value.get("query") or "main"),
        "root": str(value.get("root") or ""),
        "path": str(value.get("path") or ""),
        "notes": str(value.get("notes") or ""),
    }


def _run_target(
    target: dict[str, Any],
    *,
    outdir: Path,
    repos_root: Path,
    codeprism: Sequence[str],
    limit: int,
    max_tokens: int,
) -> dict[str, Any]:
    slug = str(target["slug"])
    target_root = _target_root(target, repos_root)
    artifact_dir = outdir / slug
    artifact_dir.mkdir(parents=True, exist_ok=True)
    result_path = artifact_dir / "result.json"
    log_path = artifact_dir / "prime.log"
    base = _base_result(target, target_root, artifact_dir, log_path)

    if not target_root.exists():
        missing = {
            **base,
            "status": "missing",
            "clone_hint": _clone_hint(target, repos_root),
        }
        result_path.write_text(json.dumps(missing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return missing

    command = [
        *codeprism,
        "prime",
        str(target["query"]),
        "--root",
        str(target_root),
        "--artifact-dir",
        str(artifact_dir),
        "--readonly-root",
        "--limit",
        str(limit),
        "--max-tokens",
        str(max_tokens),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    log_path.write_text(
        "$ " + _join_command(command) + "\n\n" + run.stdout + run.stderr,
        encoding="utf-8",
    )
    parsed = _parse_prime_output(run.stdout)
    manifest = _read_manifest(parsed.get("manifest"))
    status = "passed" if run.returncode == 0 else "failed"
    result = {
        **base,
        "status": status,
        "returncode": run.returncode,
        "metrics": _metrics_from(parsed, manifest),
    }
    if run.returncode != 0:
        result["error"] = (run.stderr or run.stdout).strip()[:1000]
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _base_result(
    target: dict[str, Any],
    target_root: Path,
    artifact_dir: Path,
    log_path: Path,
) -> dict[str, Any]:
    return {
        "name": str(target["name"]),
        "slug": str(target["slug"]),
        "url": str(target.get("url") or ""),
        "query": str(target["query"]),
        "root": str(target_root),
        "artifact_dir": str(artifact_dir),
        "log": str(log_path),
        "notes": str(target.get("notes") or ""),
    }


def _target_root(target: dict[str, Any], repos_root: Path) -> Path:
    explicit = str(target.get("root") or "").strip()
    if explicit:
        return _resolve_path(explicit, Path.cwd())
    path = str(target.get("path") or target["slug"])
    return (repos_root / path).resolve()


def _parse_prime_output(stdout: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    label_map = {
        "Wrote slice": "slice_markdown",
        "Brief": "slice_brief",
        "Manifest": "manifest",
    }
    for line in stdout.splitlines():
        for label, key in label_map.items():
            prefix = f"{label}: " if label != "Wrote slice" else f"{label} "
            if line.startswith(prefix):
                parsed[key] = line[len(prefix) :].strip()
        _match_int(parsed, line, "source_estimated_tokens", r"Source estimate: ([0-9,]+) tokens")
        _match_int(
            parsed,
            line,
            "full_context_estimated_tokens",
            r"Full context estimate: ([0-9,]+) tokens",
        )
        _match_int(parsed, line, "slice_estimated_tokens", r"Slice estimate: ([0-9,]+) tokens")
        _match_int(parsed, line, "brief_estimated_tokens", r"Brief estimate: ([0-9,]+) tokens")
        _match_float(parsed, line, "estimated_saving_percent", r"Estimated saving: ([0-9.]+)%")
        included = re.search(r"Included: ([0-9,]+) files, ([0-9,]+) symbols, ([0-9,]+) edges", line)
        if included:
            parsed["file_count"] = _as_int(included.group(1))
            parsed["symbol_count"] = _as_int(included.group(2))
            parsed["edge_count"] = _as_int(included.group(3))
        if line.startswith("Slice budget:"):
            parsed["truncated"] = True
    return parsed


def _read_manifest(path_value: object) -> dict[str, Any]:
    if not isinstance(path_value, str) or not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _metrics_from(parsed: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    metrics = {
        "source_estimated_tokens": parsed.get("source_estimated_tokens"),
        "full_context_estimated_tokens": manifest.get(
            "full_context_estimated_tokens", parsed.get("full_context_estimated_tokens")
        ),
        "slice_estimated_tokens": manifest.get("estimated_tokens", parsed.get("slice_estimated_tokens")),
        "brief_estimated_tokens": manifest.get(
            "brief_estimated_tokens", parsed.get("brief_estimated_tokens")
        ),
        "estimated_saving_percent": parsed.get("estimated_saving_percent"),
        "file_count": manifest.get("file_count", parsed.get("file_count")),
        "symbol_count": manifest.get("symbol_count", parsed.get("symbol_count")),
        "edge_count": manifest.get("edge_count", parsed.get("edge_count")),
        "truncated": bool(parsed.get("truncated") or manifest.get("truncated")),
        "slice_markdown": manifest.get("markdown", parsed.get("slice_markdown")),
        "slice_brief": manifest.get("brief", parsed.get("slice_brief")),
        "slice_manifest": parsed.get("manifest"),
    }
    return {key: value for key, value in metrics.items() if value is not None}


def _format_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CodePrism Field Notes",
        "",
        "Field notes are local measurements for public repo checkouts. They are useful for product direction, but they are not release fixture guarantees.",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "| Target | Status | Source tokens | Slice tokens | Saving | Artifacts |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for result in summary["results"]:
        metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}
        source = _fmt_int(metrics.get("source_estimated_tokens"))
        slice_tokens = _fmt_int(metrics.get("slice_estimated_tokens"))
        saving = _fmt_percent(metrics.get("estimated_saving_percent"))
        artifact = result.get("artifact_dir", "")
        lines.append(
            "| "
            f"{result['name']} | "
            f"{result['status']} | "
            f"{source} | "
            f"{slice_tokens} | "
            f"{saving} | "
            f"`{artifact}` |"
        )
    lines.extend(
        [
            "",
            "## Missing Targets",
            "",
        ]
    )
    missing = [result for result in summary["results"] if result["status"] == "missing"]
    if missing:
        lines.extend(f"- {result['name']}: `{result['clone_hint']}`" for result in missing)
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def _summarize(results: Sequence[dict[str, Any]]) -> dict[str, int]:
    return {
        "target_count": len(results),
        "passed": sum(1 for result in results if result["status"] == "passed"),
        "missing": sum(1 for result in results if result["status"] == "missing"),
        "failed": sum(1 for result in results if result["status"] == "failed"),
    }


def _clone_hint(target: dict[str, Any], repos_root: Path) -> str:
    url = str(target.get("url") or "").strip()
    destination = repos_root / str(target.get("path") or target["slug"])
    if not url:
        return f"Place a local checkout at {destination}"
    return f"git clone {url} {destination}"


def _match_int(parsed: dict[str, Any], line: str, key: str, pattern: str) -> None:
    match = re.search(pattern, line)
    if match:
        parsed[key] = _as_int(match.group(1))


def _match_float(parsed: dict[str, Any], line: str, key: str, pattern: str) -> None:
    match = re.search(pattern, line)
    if match:
        parsed[key] = float(match.group(1))


def _as_int(value: str) -> int:
    return int(value.replace(",", ""))


def _fmt_int(value: object) -> str:
    return f"{int(value):,}" if isinstance(value, int) else ""


def _fmt_percent(value: object) -> str:
    return f"{float(value):.2f}%" if isinstance(value, (float, int)) else ""


def _resolve_path(value: str, cwd: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (cwd / path).resolve()


def _command_parts(value: str | None, default: Sequence[str]) -> list[str]:
    if not value:
        return list(default)
    return shlex.split(value)


def _join_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-").lower()
    return slug or "target"


if __name__ == "__main__":
    raise SystemExit(main())
