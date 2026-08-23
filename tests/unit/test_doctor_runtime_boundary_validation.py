from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.doctor import _check_runtime_write, run_doctor


def test_doctor_runtime_write_rejects_symlink_root(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "runtime-link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")

    result = _check_runtime_write(link)

    assert result.status == "FAIL"
    assert "symbolic link" in result.detail
    assert not tuple(target.glob("athena-doctor-*.tmp"))


def test_doctor_runtime_write_accepts_real_directory(tmp_path: Path) -> None:
    root = tmp_path / "runtime"

    result = _check_runtime_write(root)

    assert result.status == "PASS"
    assert root.is_dir()


def test_run_doctor_rejects_untyped_settings() -> None:
    with pytest.raises(ValueError):
        run_doctor(object())  # type: ignore[arg-type]


def test_run_doctor_rejects_non_boolean_startup_smoke(tmp_path: Path) -> None:
    settings = AthenaSettings(local_root=tmp_path.resolve())

    with pytest.raises(ValueError):
        run_doctor(settings, startup_smoke=1)  # type: ignore[arg-type]
