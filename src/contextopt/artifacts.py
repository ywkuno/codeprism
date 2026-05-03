from __future__ import annotations

from pathlib import Path

ARTIFACT_DIR = ".codeprism"
LEGACY_ARTIFACT_DIR = ".contextopt"
ARTIFACT_DIRS = (ARTIFACT_DIR, LEGACY_ARTIFACT_DIR)


def artifact_root(root: Path) -> Path:
    return root.resolve() / ARTIFACT_DIR


def legacy_artifact_root(root: Path) -> Path:
    return root.resolve() / LEGACY_ARTIFACT_DIR


def artifact_path(root: Path, *parts: str) -> Path:
    return artifact_root(root).joinpath(*parts)


def legacy_artifact_path(root: Path, *parts: str) -> Path:
    return legacy_artifact_root(root).joinpath(*parts)


def resolve_artifact_path(
    root: Path,
    *parts: str,
    explicit: str | None = None,
    prefer_existing_legacy: bool = True,
) -> Path:
    root = root.resolve()
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.is_absolute() else root / path
    current = artifact_path(root, *parts)
    legacy = legacy_artifact_path(root, *parts)
    if prefer_existing_legacy and legacy.exists() and not current.exists():
        return legacy
    return current


def config_path(root: Path) -> Path:
    return artifact_path(root, "config.toml")


def existing_config_path(root: Path) -> Path:
    current = config_path(root)
    if current.exists():
        return current
    legacy = legacy_artifact_path(root, "config.toml")
    return legacy if legacy.exists() else current
