from __future__ import annotations

import pytest

from athena.desktop.system_workspace import _presentation_state


@pytest.mark.parametrize(
    ("runtime_state", "ui_state"),
    (
        ("unavailable", "empty"),
        ("stale", "busy"),
        ("success", "success"),
        ("error", "error"),
    ),
)
def test_system_runtime_state_maps_to_supported_presentation_state(
    runtime_state: str,
    ui_state: str,
) -> None:
    assert _presentation_state(runtime_state) == ui_state


def test_unknown_system_runtime_state_remains_fail_closed() -> None:
    assert _presentation_state("unexpected") == "unexpected"
