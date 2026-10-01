from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

import athena.core.application as application_module
from athena.core.application import ApplicationState, AthenaApplication
from athena.core.services import ServiceManager


class _Health:
    def __init__(self) -> None:
        self.events: list[str] = []

    def mark_starting(self) -> None:
        self.events.append("starting")

    def mark_failed(self, detail: str) -> None:
        self.events.append(f"failed:{detail}")

    def mark_recovery_required(self, detail: str) -> None:
        self.events.append(f"recovery:{detail}")


class _Service:
    def __init__(self, events: list[str], *, fail_stop: bool = False) -> None:
        self.events = events
        self.fail_stop = fail_stop

    @property
    def name(self) -> str:
        return "test-service"

    def start(self) -> None:
        self.events.append("start:service")

    def stop(self) -> None:
        self.events.append("stop:service")
        if self.fail_stop:
            raise RuntimeError("service stop failed")


class _FailingNews:
    def start(self) -> None:
        raise RuntimeError("news bootstrap failed")


def _failing_start_app(
    tmp_path: Path,
    *,
    service_events: list[str],
    fail_stop: bool = False,
) -> AthenaApplication:
    app = AthenaApplication.__new__(AthenaApplication)
    app.settings = SimpleNamespace(numeric_log_level=logging.INFO)
    app.paths = SimpleNamespace(
        database_path=tmp_path / "athena.db",
        log_root=tmp_path / "logs",
    )
    app.state = ApplicationState.STOPPED
    app.health = _Health()
    app.services = ServiceManager((_Service(service_events, fail_stop=fail_stop),))
    app.news = _FailingNews()
    return app


def _isolate_startup_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    close_events: list[str],
) -> None:
    monkeypatch.setattr(application_module, "inspect_database_read_only", lambda _path: None)
    monkeypatch.setattr(application_module, "configure_logging", lambda _level: None)
    monkeypatch.setattr(
        application_module,
        "configure_jsonl_logging",
        lambda _path, *, level: None,
    )
    monkeypatch.setattr(
        application_module,
        "close_jsonl_logging",
        lambda: close_events.append("close:jsonl"),
    )


def test_late_startup_failure_rolls_back_started_services(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service_events: list[str] = []
    close_events: list[str] = []
    app = _failing_start_app(tmp_path, service_events=service_events)
    _isolate_startup_side_effects(monkeypatch, close_events)

    with pytest.raises(RuntimeError, match="news bootstrap failed"):
        app.start(run_startup_maintenance=False)

    assert service_events == ["start:service", "stop:service"]
    assert app.services.started_service_names == ()
    assert app.state is ApplicationState.FAILED
    assert app.health.events == ["starting", "failed:news bootstrap failed"]
    assert close_events == ["close:jsonl"]


def test_startup_rollback_failure_does_not_replace_primary_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    service_events: list[str] = []
    close_events: list[str] = []
    app = _failing_start_app(
        tmp_path,
        service_events=service_events,
        fail_stop=True,
    )
    _isolate_startup_side_effects(monkeypatch, close_events)
    caplog.set_level(logging.ERROR, logger="athena.core.application")

    with pytest.raises(RuntimeError, match="news bootstrap failed"):
        app.start(run_startup_maintenance=False)

    assert service_events == ["start:service", "stop:service"]
    assert app.services.started_service_names == ("test-service",)
    assert app.state is ApplicationState.FAILED
    assert "ATHENA Core startup rollback failed" in caplog.text
    assert close_events == ["close:jsonl"]
