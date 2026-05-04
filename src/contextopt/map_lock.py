from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


class MapLockTimeout(TimeoutError):
    def __init__(self, lock_path: Path, timeout_s: float):
        super().__init__(f"CodePrism map is locked at {lock_path} after {timeout_s:g}s.")
        self.lock_path = lock_path
        self.timeout_s = timeout_s


def map_lock_path(db_path: Path) -> Path:
    return db_path.parent / "context.lock"


@contextmanager
def acquire_map_lock(
    lock_path: Path,
    *,
    timeout_s: float = 30.0,
    stale_after_s: float = 600.0,
    poll_s: float = 0.1,
    reason: str = "map",
) -> Iterator[Path]:
    lock_path = Path(lock_path)
    deadline = time.monotonic() + max(timeout_s, 0)
    owns_lock = False

    while True:
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if _remove_stale_lock(lock_path, stale_after_s):
                continue
            if timeout_s <= 0 or time.monotonic() >= deadline:
                raise MapLockTimeout(lock_path, timeout_s)
            sleep_s = min(max(poll_s, 0.01), max(deadline - time.monotonic(), 0.01))
            time.sleep(sleep_s)
            continue

        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "pid": os.getpid(),
                    "reason": reason,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                handle,
                sort_keys=True,
            )
        owns_lock = True
        break

    try:
        yield lock_path
    finally:
        if owns_lock:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def _remove_stale_lock(lock_path: Path, stale_after_s: float) -> bool:
    if stale_after_s <= 0:
        return False
    try:
        age_s = time.time() - lock_path.stat().st_mtime
    except FileNotFoundError:
        return True
    if age_s < stale_after_s:
        return False
    try:
        lock_path.unlink()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True
