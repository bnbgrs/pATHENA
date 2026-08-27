from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.desktop.research_workspace import ResearchWorkspace


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


@pytest.mark.parametrize("state", ["queued", "waiting", "running", "paused"])
def test_non_terminal_research_states_can_cancel(
    qt_app: QApplication,
    state: str,
) -> None:
    workspace = ResearchWorkspace()
    workspace._selected_job_id = "11111111-1111-1111-1111-111111111111"
    workspace._selected_job_state = state

    workspace._sync_cancel_button()

    assert workspace.cancel_button.isEnabled()
    assert workspace.cancel_button.property("pathenaResearchCancelAvailable") is True
    assert state in workspace.cancel_button.accessibleDescription()


@pytest.mark.parametrize(
    "state",
    ["cancel_requested", "cancelled", "failed", "completed"],
)
def test_terminal_or_requested_research_states_cannot_cancel_again(
    qt_app: QApplication,
    state: str,
) -> None:
    workspace = ResearchWorkspace()
    workspace._selected_job_id = "22222222-2222-2222-2222-222222222222"
    workspace._selected_job_state = state

    workspace._sync_cancel_button()

    assert not workspace.cancel_button.isEnabled()
    assert workspace.cancel_button.property("pathenaResearchCancelAvailable") is False
    assert "22222222" in workspace.cancel_button.accessibleDescription()
    if state == "cancel_requested":
        assert "cancellation requested" in workspace.cancel_button.accessibleDescription()
    else:
        assert state in workspace.cancel_button.accessibleDescription()


def test_no_research_selection_explains_cancel_blocker(qt_app: QApplication) -> None:
    workspace = ResearchWorkspace()

    workspace._sync_cancel_button()

    assert not workspace.cancel_button.isEnabled()
    assert "Select a research run" in workspace.cancel_button.accessibleDescription()
