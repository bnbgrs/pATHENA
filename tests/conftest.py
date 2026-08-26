"""Shared pytest safeguards for filesystem-heavy pATHENA tests."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

_RESERVE_FILENAME = "emergency.reserve"


def _remove_test_reserve(path: Path) -> None:
    """Remove one test-owned reserve without following a redirecting boundary."""
    if path.is_symlink():
        path.unlink(missing_ok=True)
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def release_test_emergency_reserves(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    """Keep real reserve semantics per test without exhausting the CI volume.

    Production reserves intentionally persist across application restarts. Pytest,
    however, retains every function-scoped temporary directory until the session
    finishes. Hundreds of independent application fixtures would therefore retain
    hundreds of physical reserves concurrently and can push the CI volume into the
    real EMERGENCY disk-pressure state. Cleanup happens only after each test has
    completed, so restart/persistence assertions inside a test still exercise the
    real reserve implementation unchanged.
    """
    yield

    base_temp = tmp_path_factory.getbasetemp()
    for reserve in base_temp.rglob(_RESERVE_FILENAME):
        _remove_test_reserve(reserve)
