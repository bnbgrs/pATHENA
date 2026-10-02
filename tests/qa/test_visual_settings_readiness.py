from __future__ import annotations

import pytest

from scripts.render_pathena_ui_snapshot_sequential import _settings_state_is_ready


@pytest.mark.parametrize(
    ("snapshot_ready", "refreshing", "news_ready", "status_text"),
    [
        (False, False, True, "Ready"),
        (True, True, True, "Ready"),
        (True, False, False, "Ready"),
        (True, False, True, ""),
        (True, False, True, "Connecting…"),
        (True, False, True, "LOCAL / CORE DISCONNECTED"),
    ],
)
def test_settings_visual_state_rejects_transitional_runtime(
    snapshot_ready: bool,
    refreshing: bool,
    news_ready: bool,
    status_text: str,
) -> None:
    assert not _settings_state_is_ready(
        snapshot_ready=snapshot_ready,
        refreshing=refreshing,
        news_ready=news_ready,
        status_text=status_text,
    )


def test_settings_visual_state_accepts_settled_snapshot() -> None:
    assert _settings_state_is_ready(
        snapshot_ready=True,
        refreshing=False,
        news_ready=True,
        status_text="Model error",
    )
