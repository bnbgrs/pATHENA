from pathlib import Path

import pytest

from athena import doctor


def test_optional_storage_root_reports_writable_directory(tmp_path: Path) -> None:
    root = tmp_path / "archive"
    root.mkdir()

    check = doctor._check_optional_storage_root(
        "archive-root",
        root,
        missing_status="PASS",
        missing_detail="not configured",
    )

    assert check.status == "PASS"
    assert check.detail == f"writable: {root}"


def test_optional_storage_root_warns_when_write_probe_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "backup"
    root.mkdir()

    def fail_probe(*args: object, **kwargs: object) -> object:
        raise OSError("access denied")

    monkeypatch.setattr(doctor.tempfile, "NamedTemporaryFile", fail_probe)

    check = doctor._check_optional_storage_root(
        "backup-root",
        root,
        missing_status="WARN",
        missing_detail="not configured",
    )

    assert check.status == "WARN"
    assert "not writable" in check.detail
    assert "access denied" in check.detail
