from __future__ import annotations

import pytest

from scripts.render_pathena_ui_snapshot_sequential import _settings_state_is_ready


@pytest.mark.parametrize(
    (
        "snapshot_ready",
        "refreshing",
        "news_ready",
        "status_text",
        "lmstudio_status",
        "lmstudio_busy",
    ),
    [
        (False, False, True, "Ready", "LM Studio runtime · lms CLI not found", False),
        (True, True, True, "Ready", "LM Studio runtime · lms CLI not found", False),
        (True, False, False, "Ready", "LM Studio runtime · lms CLI not found", False),
        (True, False, True, "", "LM Studio runtime · lms CLI not found", False),
        (True, False, True, "Connecting…", "LM Studio runtime · lms CLI not found", False),
        (
            True,
            False,
            True,
            "LOCAL / CORE DISCONNECTED",
            "LM Studio runtime · lms CLI not found",
            False,
        ),
        (True, False, True, "Ready", "LM Studio runtime · awaiting Core", False),
        (True, False, True, "Ready", "LM Studio runtime · waiting for local Core", False),
        (
            True,
            False,
            True,
            "Ready",
            "LM Studio runtime · Starting local LM Studio server …",
            True,
        ),
    ],
)
def test_settings_visual_state_rejects_transitional_runtime(
    snapshot_ready: bool,
    refreshing: bool,
    news_ready: bool,
    status_text: str,
    lmstudio_status: str,
    lmstudio_busy: bool,
) -> None:
    assert not _settings_state_is_ready(
        snapshot_ready=snapshot_ready,
        refreshing=refreshing,
        news_ready=news_ready,
        status_text=status_text,
        lmstudio_status=lmstudio_status,
        lmstudio_busy=lmstudio_busy,
    )


def test_settings_visual_state_accepts_settled_snapshot() -> None:
    assert _settings_state_is_ready(
        snapshot_ready=True,
        refreshing=False,
        news_ready=True,
        status_text="Model error",
        lmstudio_status=(
            "LM Studio runtime · lms CLI not found; install/enable LM Studio CLI integration"
        ),
        lmstudio_busy=False,
    )
