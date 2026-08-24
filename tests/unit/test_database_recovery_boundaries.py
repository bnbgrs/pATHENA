from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.recovery as recovery_module
from athena.storage.recovery import (
    DatabasePreflightReport,
    DatabaseRecoveryRequiredError,
    inspect_database_read_only,
)


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlink unavailable: {exc}")


def test_preflight_rejects_non_path() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        inspect_database_read_only("athena.db")  # type: ignore[arg-type]


def test_preflight_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(DatabaseRecoveryRequiredError, match="symbolic-link ancestor"):
        inspect_database_read_only(link / "athena.db")


def test_preflight_rejects_shared_reparse_boundary_ancestor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    boundary = tmp_path / "boundary"
    boundary.mkdir()
    original = recovery_module.is_link_boundary

    def classified_boundary(path: Path) -> bool:
        return path == boundary or original(path)

    monkeypatch.setattr(
        recovery_module,
        "is_link_boundary",
        classified_boundary,
    )

    with pytest.raises(DatabaseRecoveryRequiredError, match="reparse-point ancestor"):
        inspect_database_read_only(boundary / "athena.db")


def test_missing_database_report_has_no_schema_metadata(tmp_path: Path) -> None:
    report = inspect_database_read_only(tmp_path / "athena.db")
    assert report.exists is False
    assert report.application_id is None
    assert report.schema_version is None


def test_report_rejects_existing_database_without_metadata(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires application_id"):
        DatabasePreflightReport(
            path=tmp_path / "athena.db",
            exists=True,
            application_id=None,
            schema_version=None,
            wal_present=False,
            shm_present=False,
        )


def test_report_rejects_bool_application_id(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="application_id"):
        DatabasePreflightReport(
            path=tmp_path / "athena.db",
            exists=True,
            application_id=True,  # type: ignore[arg-type]
            schema_version=1,
            wal_present=False,
            shm_present=False,
        )
