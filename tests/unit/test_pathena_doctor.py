from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.doctor import DoctorCheck, run_doctor


def _settings(root: Path) -> AthenaSettings:
    return AthenaSettings(
        local_root=root,
        lm_studio_base_url="http://127.0.0.1:1234",
        model_request_timeout_seconds=0.05,
        model_generation_timeout_seconds=1.0,
    )


def test_doctor_bootstraps_fresh_runtime_without_model(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "athena.doctor._check_model",
        lambda _settings: DoctorCheck("lm-studio", "WARN", "offline for test"),
    )

    report = run_doctor(_settings(tmp_path / "runtime"), startup_smoke=True)

    assert report.core_ready is True
    assert report.model_ready is False
    statuses = {check.name: check.status for check in report.checks}
    assert statuses["python"] == "PASS"
    assert statuses["runtime-write"] == "PASS"
    assert statuses["database-preflight"] == "PASS"
    assert statuses["core-startup"] == "PASS"
    assert statuses["core-shutdown"] == "PASS"
    assert (tmp_path / "runtime" / "state" / "athena.db").is_file()


def test_doctor_fails_closed_for_corrupt_existing_database(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "athena.doctor._check_model",
        lambda _settings: DoctorCheck("lm-studio", "WARN", "offline for test"),
    )
    database_path = tmp_path / "runtime" / "state" / "athena.db"
    database_path.parent.mkdir(parents=True)
    database_path.write_bytes(b"not-a-sqlite-database")

    report = run_doctor(_settings(tmp_path / "runtime"), startup_smoke=True)

    assert report.core_ready is False
    statuses = {check.name: check.status for check in report.checks}
    assert statuses["database-preflight"] == "FAIL"
    assert statuses["core-startup"] == "SKIP"
