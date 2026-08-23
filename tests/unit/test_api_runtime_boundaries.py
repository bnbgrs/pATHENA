from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from athena.api.runtime import ApiRuntimeError, LocalApiRuntime


@pytest.mark.parametrize("port", [True, False, 1234.5, "1234", 0, 65536])
def test_publish_rejects_non_integer_or_out_of_range_port(
    tmp_path: Path,
    port: Any,
) -> None:
    runtime = LocalApiRuntime(tmp_path / "api")

    with pytest.raises(ValueError, match="integer between 1 and 65535"):
        runtime.publish(port=port)  # type: ignore[arg-type]

    assert not runtime.discovery_path.exists()
    assert not runtime.token_path.exists()


def test_authenticate_rejects_non_string_token_without_exception(tmp_path: Path) -> None:
    runtime = LocalApiRuntime(tmp_path / "api")
    runtime.publish(port=1234)

    assert runtime.authenticate(b"token") is False  # type: ignore[arg-type]
    assert runtime.authenticate(1234) is False  # type: ignore[arg-type]


def test_clear_attempts_token_removal_even_when_discovery_unlink_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = LocalApiRuntime(tmp_path / "api")
    runtime.publish(port=1234)
    original_unlink = Path.unlink

    def guarded_unlink(path: Path, *args: Any, **kwargs: Any) -> None:
        if path == runtime.discovery_path:
            raise PermissionError("blocked discovery")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", guarded_unlink)

    with pytest.raises(ApiRuntimeError, match="runtime file"):
        runtime.clear()

    assert runtime.discovery_path.exists()
    assert not runtime.token_path.exists()
    assert runtime.authenticate("anything") is False


def test_publish_rejects_symlink_runtime_root(tmp_path: Path) -> None:
    real_root = tmp_path / "real"
    real_root.mkdir()
    link_root = tmp_path / "link"
    try:
        link_root.symlink_to(real_root, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")

    runtime = LocalApiRuntime(link_root)

    with pytest.raises(ApiRuntimeError, match="must not be a symlink"):
        runtime.publish(port=1234)

    assert not (real_root / "core-api.token").exists()
