from __future__ import annotations

import os
from pathlib import Path

import pytest

from athena.desktop.lmstudio_runtime import (
    _accepted_model_load_id,
    _coerce_idle_minutes,
    _command_timeout_ms,
    _continue_after_failed_step,
    _CommandStep,
    _endpoint,
    _endpoint_port,
    _find_lms,
    _model_confirmation_action,
    _process_command,
    _server_start_steps,
    _should_attempt_auto_load,
    _should_attempt_auto_start,
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://127.0.0.1:1234", 1234),
        ("http://localhost:4321", 4321),
        ("http://[::1]:7777", 7777),
        ("http://localhost", 80),
    ],
)
def test_endpoint_port_accepts_only_loopback_http(url: str, expected: int) -> None:
    assert _endpoint_port(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:1234",
        "http://example.com:1234",
        "file:///tmp/lmstudio",
        "http://127.0.0.1:99999",
    ],
)
def test_endpoint_port_rejects_unsafe_or_invalid_targets(url: str) -> None:
    with pytest.raises(ValueError):
        _endpoint_port(url)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://127.0.0.1:1234", ("127.0.0.1", 1234)),
        ("http://localhost:4321", ("127.0.0.1", 4321)),
        ("http://[::1]:7777", ("::1", 7777)),
    ],
)
def test_endpoint_preserves_loopback_bind_identity(
    url: str, expected: tuple[str, int]
) -> None:
    assert _endpoint(url) == expected


def test_headless_server_start_is_daemon_first_and_endpoint_bound() -> None:
    daemon, server = _server_start_steps("http://[::1]:7777")
    assert daemon.operation == "daemon_up"
    assert daemon.arguments == ("daemon", "up")
    assert server.operation == "server_start"
    assert server.arguments == (
        "server",
        "start",
        "--port",
        "7777",
        "--bind",
        "::1",
    )


@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("daemon_up", 45_000),
        ("server_start", 45_000),
        ("server_stop", 45_000),
        ("model_unload", 120_000),
        ("model_load", 600_000),
    ],
)
def test_lms_cli_operations_have_bounded_timeouts(
    operation: str, expected: int
) -> None:
    assert _command_timeout_ms(operation) == expected


def test_process_command_preserves_arguments_for_native_executable() -> None:
    program, arguments = _process_command(
        "/opt/lmstudio/lms",
        ("load", "model-id", "--context-length", "8192"),
    )
    assert program == "/opt/lmstudio/lms"
    assert arguments == ["load", "model-id", "--context-length", "8192"]


@pytest.mark.skipif(os.name != "nt", reason="Windows command wrappers are Windows-only")
def test_process_command_routes_cmd_wrappers_through_comspec(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMSPEC", "C:\\Windows\\System32\\cmd.exe")
    program, arguments = _process_command(
        "C:\\Tools\\lms.cmd",
        ("server", "start", "--port", "1234"),
    )
    assert program.endswith("cmd.exe")
    assert arguments[:4] == ["/d", "/s", "/c", "C:\\Tools\\lms.cmd"]


def test_find_lms_honors_explicit_executable_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    executable = tmp_path / ("lms.exe" if os.name == "nt" else "lms")
    executable.write_text("stub", encoding="utf-8")
    monkeypatch.setenv("ATHENA_LMS_EXECUTABLE", str(executable))
    assert _find_lms() == str(executable.resolve())


@pytest.mark.skipif(os.name != "nt", reason="cmd.exe wrappers are Windows-only")
def test_cmd_wrapper_rejects_shell_metacharacters() -> None:
    with pytest.raises(ValueError, match="unsafe"):
        _process_command(
            "C:\\Tools\\lms.cmd",
            ("load", "unsafe&model"),
        )


@pytest.mark.parametrize(
    ("loaded", "enabled", "attempted_model_id", "busy", "expected"),
    [
        (False, True, None, False, True),
        (False, True, "other-model", False, True),
        (False, True, "model-id", False, False),
        (True, True, None, False, False),
        (False, False, None, False, False),
        (False, True, None, True, False),
    ],
)
def test_auto_load_attempts_once_per_selected_model(
    loaded: bool,
    enabled: bool,
    attempted_model_id: str | None,
    busy: bool,
    expected: bool,
) -> None:
    assert (
        _should_attempt_auto_load(
            model_id="model-id",
            loaded=loaded,
            enabled=enabled,
            attempted_model_id=attempted_model_id,
            busy=busy,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("provider_ready", "enabled", "attempted", "busy", "expected"),
    [
        (False, True, False, False, True),
        (True, True, False, False, False),
        (False, False, False, False, False),
        (False, True, True, False, False),
        (False, True, False, True, False),
    ],
)
def test_auto_start_attempts_once_per_provider_outage(
    provider_ready: bool,
    enabled: bool,
    attempted: bool,
    busy: bool,
    expected: bool,
) -> None:
    assert (
        _should_attempt_auto_start(
            provider_ready=provider_ready,
            enabled=enabled,
            attempted=attempted,
            busy=busy,
        )
        is expected
    )



def test_model_load_waits_for_core_confirmation_before_becoming_ready() -> None:
    action, remaining = _model_confirmation_action(
        pending_model_id="model-id",
        selected_model_id="model-id",
        loaded=False,
        refreshes_remaining=2,
    )
    assert (action, remaining) == ("refresh", 1)

    action, remaining = _model_confirmation_action(
        pending_model_id="model-id",
        selected_model_id="model-id",
        loaded=True,
        refreshes_remaining=remaining,
    )
    assert (action, remaining) == ("confirmed", 0)


def test_model_load_confirmation_failure_is_bounded() -> None:
    remaining = 2
    actions: list[str] = []
    for _ in range(3):
        action, remaining = _model_confirmation_action(
            pending_model_id="model-id",
            selected_model_id="model-id",
            loaded=False,
            refreshes_remaining=remaining,
        )
        actions.append(action)
    assert actions == ["refresh", "refresh", "failed"]
    assert remaining == 0


def test_model_confirmation_ignores_a_different_selected_model() -> None:
    assert _model_confirmation_action(
        pending_model_id="old-model",
        selected_model_id="new-model",
        loaded=False,
        refreshes_remaining=3,
    ) == ("none", 3)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (30, 30),
        (0, 0),
        (-1, 0),
        (2000, 1440),
        ("30", 30),
        ("45", 45),
        ("-1", 0),
        (None, 30),
        (True, 30),
    ],
)
def test_idle_minutes_requires_a_genuine_bounded_integer(
    value: object, expected: int
) -> None:
    assert _coerce_idle_minutes(value) == expected


def test_pending_model_identity_comes_only_from_completed_load_command() -> None:
    load = _CommandStep(
        operation="model_load",
        arguments=("load", "model-id", "--context-length", "8192"),
        status="Loading model",
    )
    assert _accepted_model_load_id(load) == "model-id"

    not_load = _CommandStep(
        operation="server_start",
        arguments=("server", "start"),
        status="Starting server",
    )
    assert _accepted_model_load_id(not_load) is None

    malformed = _CommandStep(
        operation="model_load",
        arguments=("load", ""),
        status="Loading model",
    )
    assert _accepted_model_load_id(malformed) is None


def test_restart_continues_only_after_a_failed_stop_step() -> None:
    stop = _CommandStep("server_stop", ("server", "stop"), "Stopping server")
    load = _CommandStep("model_load", ("load", "model-id"), "Loading model")
    assert _continue_after_failed_step(stop) is True
    assert _continue_after_failed_step(load) is False


def test_find_lms_discovers_standard_per_user_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("ATHENA_LMS_EXECUTABLE", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    executable = (
        tmp_path
        / ".lmstudio"
        / "bin"
        / ("lms.exe" if os.name == "nt" else "lms")
    )
    executable.parent.mkdir(parents=True)
    executable.write_text("stub", encoding="utf-8")
    assert _find_lms() == str(executable.resolve())
