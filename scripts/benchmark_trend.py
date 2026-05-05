from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a CodePrism benchmark trend report from a local baseline "
            "or a downloaded GitHub Actions artifact."
        )
    )
    parser.add_argument(
        "--repo",
        default="kunolabs/codeprism",
        help="GitHub owner/repo used when downloading a baseline artifact.",
    )
    parser.add_argument("--workflow", default="tests.yml")
    parser.add_argument("--run-id", help="Specific GitHub Actions run ID to download.")
    parser.add_argument("--python-version", default="3.12")
    parser.add_argument(
        "--artifact-name",
        help="Artifact name. Defaults to codeprism-benchmarks-py<PYTHON_VERSION>.",
    )
    parser.add_argument(
        "--baseline-suite",
        help="Existing benchmark-suite JSON to use instead of downloading an artifact.",
    )
    parser.add_argument(
        "--current-suite",
        help="Existing benchmark-suite JSON to compare instead of running the suite.",
    )
    parser.add_argument("--fixtures-root", default="examples/benchmarks")
    parser.add_argument("--outdir", default=".codeprism/benchmark-trends")
    parser.add_argument("--regression-threshold", type=float, default=5.0)
    parser.add_argument("--fail-on-regression", action="store_true")
    parser.add_argument(
        "--gh-command",
        help="Command used to invoke GitHub CLI. Defaults to gh.",
    )
    parser.add_argument(
        "--codeprism-command",
        help="Command used to invoke CodePrism. Defaults to this Python running contextopt.cli.",
    )
    args = parser.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    codeprism = _command_parts(args.codeprism_command, [sys.executable, "-m", "contextopt.cli"])

    try:
        baseline_suite = _resolve_baseline_suite(args, outdir)
        current_suite = _resolve_current_suite(args, outdir, codeprism)
        comparison = outdir / "comparison.md"
        compare_command = [
            *codeprism,
            "benchmark-compare",
            str(baseline_suite),
            str(current_suite),
            "--out",
            str(comparison),
            "--regression-threshold",
            str(args.regression_threshold),
        ]
        if args.fail_on_regression:
            compare_command.append("--fail-on-regression")
        compare_result = _run(compare_command, check=False)
        if compare_result.returncode != 0:
            return compare_result.returncode
    except TrendError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Benchmark trend ready.")
    print(f"Baseline: {baseline_suite}")
    print(f"Current: {current_suite}")
    print(f"Comparison: {comparison}")
    return 0


class TrendError(Exception):
    """Raised when the benchmark trend helper cannot prepare inputs."""


def _resolve_baseline_suite(args: argparse.Namespace, outdir: Path) -> Path:
    if args.baseline_suite:
        path = Path(args.baseline_suite)
        _assert_suite_json(path)
        return path

    gh = _command_parts(args.gh_command, ["gh"])
    artifact_name = args.artifact_name or f"codeprism-benchmarks-py{args.python_version}"
    run_id = args.run_id or _latest_successful_run_id(gh, args.repo, args.workflow)
    download_dir = outdir / "baseline-artifact"
    if download_dir.exists():
        shutil.rmtree(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    _run(
        [
            *gh,
            "run",
            "download",
            run_id,
            "--repo",
            args.repo,
            "--name",
            artifact_name,
            "--dir",
            str(download_dir),
        ]
    )
    suite = _find_suite_json(download_dir)
    if suite is None:
        raise TrendError(f"No benchmark suite JSON found in downloaded artifact: {download_dir}")
    return suite


def _resolve_current_suite(
    args: argparse.Namespace, outdir: Path, codeprism: Sequence[str]
) -> Path:
    if args.current_suite:
        path = Path(args.current_suite)
        _assert_suite_json(path)
        return path
    current = outdir / "current-suite.json"
    _run(
        [
            *codeprism,
            "benchmark-suite",
            args.fixtures_root,
            "--out",
            str(current),
        ]
    )
    _assert_suite_json(current)
    return current


def _latest_successful_run_id(gh: Sequence[str], repo: str, workflow: str) -> str:
    result = _run(
        [
            *gh,
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            workflow,
            "--status",
            "success",
            "--limit",
            "1",
            "--json",
            "databaseId",
        ],
        capture=True,
    )
    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TrendError(f"GitHub CLI returned invalid run JSON: {exc}") from exc
    if not runs:
        raise TrendError(f"No successful workflow runs found for {repo} {workflow}")
    run_id = runs[0].get("databaseId")
    if not run_id:
        raise TrendError("Latest successful workflow run did not include a databaseId")
    return str(run_id)


def _find_suite_json(root: Path) -> Path | None:
    for path in sorted(root.rglob("suite.json")):
        if _is_suite_json(path):
            return path
    for path in sorted(root.rglob("*.json")):
        if _is_suite_json(path):
            return path
    return None


def _assert_suite_json(path: Path) -> None:
    if not path.exists():
        raise TrendError(f"Benchmark suite JSON not found: {path}")
    if not _is_suite_json(path):
        raise TrendError(f"Not a benchmark-suite JSON file: {path}")


def _is_suite_json(path: Path) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and isinstance(payload.get("fixtures"), list)


def _command_parts(value: str | None, default: Sequence[str]) -> list[str]:
    if not value:
        return list(default)
    return shlex.split(value)


def _run(
    command: Sequence[str], *, capture: bool = False, check: bool = True
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            list(command),
            capture_output=capture,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise TrendError(f"Command not found: {command[0]}") from exc
    if check and result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        suffix = f": {details}" if details else ""
        raise TrendError(f"Command failed ({result.returncode}) {' '.join(command)}{suffix}")
    if not capture and result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.stdout:
            print(result.stdout, end="")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
