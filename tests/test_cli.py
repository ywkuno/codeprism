from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_init_writes_default_config(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "contextopt.cli", "init", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    config = tmp_path / ".contextopt" / "config.toml"
    assert config.read_text(encoding="utf-8") == (
        'max_file_bytes = 500000\nignore = ["node_modules", ".git", "dist", "build", ".next"]\n'
    )
