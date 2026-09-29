from __future__ import annotations

import os
from pathlib import Path

import pytest

from athena.desktop.lmstudio_runtime import (
    _CommandStep,
    _accepted_model_load_id,
    _coerce_idle_minutes,
    _endpoint_port,
    _find_lms,
    _model_verification_action,
    _process_command,
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


def test_model_load_verification_waits_for_core_confirmation() -> None:
    assert (
        _model_verification_action(
            loaded=False,
            refreshes=0,
            retries=0,
        )
        == "wait"
    )
    assert (
        _model_verification_action(
            loaded=True,
            refreshes=1,
            retries=0,
        )
        == "confirmed"
    )


def test_model_load_verification_has_bounded_retry_and_failure() -> None:
    assert (
        _model_verification_action(
            loaded=False,
            refreshes=5,
            retries=0,
        )
        == "retry"
    )
    assert (
        _model_verification_action(
            loaded=False,
            refreshes=5,
            retries=1,
        )
        == "failed"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (30, 30),
        (0, 0),
        (-1, 0),
        (2000, 1440),
        ("30", 30),
        (None, 30),
        (True, 30),
    ],
)
def test_idle_minutes_coercion_is_typed_and_bounded(value: object, expected: int) -> None:
    assert _coerce_idle_minutes(value) == expected


def test_pending_model_identity_is_derived_only_from_accepted_load_step() -> None:
    accepted = _CommandStep(
        operation="model_load",
        arguments=("load", "model-id", "--context-length", "8192"),
        status="Loading model",
    )
    assert _accepted_model_load_id(accepted) == "model-id"

    server_step = _CommandStep(
        operation="server_start",
        arguments=("server", "start", "--port", "1234"),
        status="Starting server",
    )
    assert _accepted_model_load_id(server_step) is None

    malformed = _CommandStep(
        operation="model_load",
        arguments=("load", ""),
        status="Loading model",
    )
    assert _accepted_model_load_id(malformed) is None


def test_model_verification_never_confirms_without_core_loaded_state() -> None:
    assert _model_verification_action(
        loaded=False,
        refreshes=0,
        retries=0,
    ) == "wait"
    assert _model_verification_action(
        loaded=False,
        refreshes=5,
        retries=0,
    ) == "retry"
