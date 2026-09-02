from __future__ import annotations

import os
from typing import cast

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.api.contracts import (
    ChatSummaryResponse,
    HealthResponse,
    ModelResponse,
    ProviderHealthResponse,
)
from athena.desktop.api_controller import DesktopApiSnapshot, SnapshotFreshness
from athena.desktop.app import create_application
from athena.desktop.system_runtime_overview import project_system_runtime
from athena.desktop.system_workspace import SystemWorkspace


def _app() -> QApplication:
    return create_application(["pathena-system-runtime-overview-test"])


_READY_PROVIDER = ProviderHealthResponse(
    provider="lm_studio",
    status="ready",
    detail=None,
)


def _snapshot(
    *,
    provider: ProviderHealthResponse | None = _READY_PROVIDER,
    model_freshness: str | None = None,
    chat_freshness: str | None = None,
    model_error: str | None = None,
) -> DesktopApiSnapshot:
    return DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=provider,
        models=(
            ModelResponse(
                provider="lm_studio",
                backend_model_id="qwen",
                display_name="Qwen",
                model_type="llm",
                context_capacity=32768,
                quantization="Q4",
                loaded=True,
                vision=False,
                trained_for_tool_use=True,
                loaded_context_length=16384,
            ),
        ),
        chats=(
            ChatSummaryResponse(
                chat_id="chat-1",
                started_at_us=1,
                ended_at_us=None,
                archive_mode="standard",
                lifecycle_state="active",
                message_count=2,
            ),
        ),
        model_error=model_error,
        model_freshness=cast(SnapshotFreshness | None, model_freshness),
        chat_freshness=cast(SnapshotFreshness | None, chat_freshness),
    )


def test_reachable_snapshot_reports_only_probe_backed_facts() -> None:
    overview = project_system_runtime(_snapshot())

    assert overview.core.value == "Ok"
    assert overview.provider.value == "Ready"
    assert overview.network.value == "Provider reachable"
    assert overview.models.value == "1"
    assert overview.storage.value == "Unavailable"
    assert "exposes no storage probe" in overview.detail
    assert overview.state == "success"


def test_unreachable_provider_and_storage_remain_explicitly_unavailable() -> None:
    overview = project_system_runtime(_snapshot(provider=None, model_error="offline"))

    assert overview.provider.value == "Unavailable"
    assert overview.network.value == "Provider unavailable"
    assert overview.models.value == "Unavailable"
    assert overview.storage.value == "Unavailable"
    assert overview.state == "unavailable"


def test_stale_snapshot_keeps_counts_but_marks_them_stale() -> None:
    overview = project_system_runtime(
        _snapshot(
            model_freshness="stale",
            chat_freshness="stale",
            model_error="last refresh failed",
        )
    )

    assert overview.provider.value == "Ready · stale"
    assert overview.models.value == "1 · stale"
    assert overview.loaded_models.value == "1 · stale"
    assert overview.chats.value == "1 · stale"
    assert overview.state == "stale"


def test_workspace_clears_live_values_on_core_failure() -> None:
    app = _app()
    workspace = SystemWorkspace(None)
    try:
        workspace.apply_snapshot(_snapshot())
        workspace.apply_failure("Core connection refused.")
        app.processEvents()

        assert workspace.runtime.value.text() == "Disconnected"
        assert workspace.storage.value.text() == "Unavailable"
        assert workspace.connectivity.value.text() == "Core unreachable"
        assert "Core connection refused" in workspace.detail.text()
    finally:
        workspace.close()
        app.processEvents()
