from pathlib import Path

import pytest

from athena.local_smoke import _assert_safe_keep_root


def test_keep_root_rejects_configured_live_runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    live_root = tmp_path / "live"
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(live_root))

    with pytest.raises(RuntimeError, match="refuses to use the configured live"):
        _assert_safe_keep_root(live_root)


def test_keep_root_accepts_separate_test_runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    live_root = tmp_path / "live"
    smoke_root = tmp_path / "smoke"
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(live_root))

    assert _assert_safe_keep_root(smoke_root) == smoke_root.resolve(strict=False)
