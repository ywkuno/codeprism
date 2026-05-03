from __future__ import annotations
import shutil
from pathlib import Path


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"copied {src} -> {dst}")


def main() -> int:
    root = Path.cwd()
    base = Path(__file__).resolve().parents[1]
    copy_file(
        base / "integrations" / "copilot" / "copilot-instructions.md",
        root / ".github" / "copilot-instructions.md",
    )
    copy_file(
        base / "integrations" / "claude-commands" / "context-map.md",
        root / ".claude" / "commands" / "context-map.md",
    )
    copy_file(
        base / "integrations" / "claude-commands" / "context-query.md",
        root / ".claude" / "commands" / "context-query.md",
    )
    print("Cortext Claude Skill folder is available under integrations/claude-skill/cortext")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
