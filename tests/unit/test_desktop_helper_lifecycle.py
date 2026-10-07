from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType

import pytest

from athena.desktop import (
    canonical_memory_cli,
    jobs_cli,
    knowledge_cli,
    research_cli,
    sources_cli,
)

_HELPERS: tuple[tuple[ModuleType, tuple[str, ...], str], ...] = (
    (canonical_memory_cli, ("merge-list",), "CANONICAL_MEMORY_ERROR"),
    (jobs_cli, ("list",), "JOBS_ERROR"),
    (knowledge_cli, ("list",), "KNOWLEDGE_ERROR"),
    (research_cli, ("list",), "RESEARCH_ERROR"),
    (sources_cli, ("list",), "SOURCES_ERROR"),
)


@dataclass
class _StorageLifecycle:
    fail_stop: bool = False
    started: int = 0
    stopped: int = 0

    def start(self) -> None:
        self.started += 1

    def stop(self) -> None:
        self.stopped += 1
        if self.fail_stop:
            raise RuntimeError("storage stop failed")


class _HelperApp:
    def __init__(self, *, fail_stop: bool = False) -> None:
        self.storage_bootstrap = _StorageLifecycle(fail_stop=fail_stop)

    def start(self, **_kwargs: object) -> None:
        raise AssertionError("Desktop helper must not start the full Core lifecycle")

    def stop(self) -> None:
        raise AssertionError("Desktop helper must not stop the full Core lifecycle")


@pytest.mark.parametrize(
    ("module", "argv", "_error_prefix"),
    _HELPERS,
    ids=(
        "canonical-memory",
        "jobs",
        "knowledge",
        "research",
        "sources",
    ),
)
def test_desktop_helpers_use_storage_only_lifecycle(
    monkeypatch,
    module: ModuleType,
    argv: tuple[str, ...],
    _error_prefix: str,
) -> None:
    app = _HelperApp()
    monkeypatch.setattr(module, "AthenaApplication", lambda: app)
    monkeypatch.setattr(module, "_run", lambda _app, _args: 0)

    result = module.main(argv)

    assert result == 0
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1


@pytest.mark.parametrize(
    ("module", "argv", "error_prefix"),
    _HELPERS,
    ids=(
        "canonical-memory",
        "jobs",
        "research",
        "sources",
    ),
)
def test_desktop_helpers_stop_storage_after_command_failure(
    monkeypatch,
    capsys,
    module: ModuleType,
    argv: tuple[str, ...],
    error_prefix: str,
) -> None:
    app = _HelperApp()
    monkeypatch.setattr(module, "AthenaApplication", lambda: app)

    def fail(_app: object, _args: object) -> int:
        raise RuntimeError("helper command failed")

    monkeypatch.setattr(module, "_run", fail)

    result = module.main(argv)

    assert result == 2
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1
    assert (
        f"{error_prefix} RuntimeError: helper command failed"
        in capsys.readouterr().err
    )


@pytest.mark.parametrize(
    ("module", "argv", "error_prefix"),
    _HELPERS,
    ids=(
        "canonical-memory",
        "jobs",
        "research",
        "sources",
    ),
)
def test_desktop_helpers_fail_closed_when_storage_shutdown_fails(
    monkeypatch,
    capsys,
    module: ModuleType,
    argv: tuple[str, ...],
    error_prefix: str,
) -> None:
    app = _HelperApp(fail_stop=True)
    monkeypatch.setattr(module, "AthenaApplication", lambda: app)
    monkeypatch.setattr(module, "_run", lambda _app, _args: 0)

    result = module.main(argv)

    assert result == 2
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1
    assert f"{error_prefix} RuntimeError: storage stop failed" in capsys.readouterr().err
