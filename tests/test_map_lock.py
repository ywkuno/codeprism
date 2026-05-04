from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from contextopt.map_lock import MapLockTimeout, acquire_map_lock


def test_map_lock_blocks_second_acquire_until_timeout(tmp_path: Path):
    lock = tmp_path / "context.lock"

    with acquire_map_lock(lock, timeout_s=0.1, poll_s=0.01, stale_after_s=60):
        assert lock.exists()
        with pytest.raises(MapLockTimeout):
            with acquire_map_lock(lock, timeout_s=0, poll_s=0.01, stale_after_s=60):
                pass

    assert not lock.exists()


def test_map_lock_replaces_stale_lock(tmp_path: Path):
    lock = tmp_path / "context.lock"
    lock.write_text('{"pid":999999,"reason":"test"}', encoding="utf-8")
    old_time = time.time() - 120
    os.utime(lock, (old_time, old_time))

    with acquire_map_lock(lock, timeout_s=0, poll_s=0.01, stale_after_s=1):
        assert lock.exists()

    assert not lock.exists()
