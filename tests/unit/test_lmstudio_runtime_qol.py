from __future__ import annotations

import os
from pathlib import Path

import pytest

from athena.desktop.lmstudio_runtime import (
    _endpoint_port,
    _find_lms,
    _model_confirmation_action,
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
