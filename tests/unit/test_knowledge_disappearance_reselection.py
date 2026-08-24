from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QPlainTextEdit

from athena.desktop.pathena_knowledge_selection_continuity import (
    KnowledgeSelectionContinuity,
)


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


class _ContinuityStub:
    def __init__(self, details: QPlainTextEdit) -> None:
        self.details = details

    def _selection_context(
        self,
        _widget: QListWidget,
    ) -> tuple[str | None, QPlainTextEdit, str]:
        return None, self.details, "Knowledge"


def test_new_selection_clears_stale_disappearance_marker(
    qt_app: QApplication,
) -> None:
    listing = QListWidget()
    details = QPlainTextEdit()
    listing.setProperty("pathenaSelectionDisappeared", "old-knowledge-id")
    details.setProperty("pathenaSelectionDisappeared", "old-knowledge-id")
    listing.setStatusTip("old disappearance message")
    current = QListWidgetItem("Replacement knowledge")

    KnowledgeSelectionContinuity._clear_disappearance_on_new_selection(
        _ContinuityStub(details),  # type: ignore[arg-type]
        listing,
        current,
    )

    assert listing.property("pathenaSelectionDisappeared") == ""
    assert details.property("pathenaSelectionDisappeared") == ""
    assert listing.statusTip() == ""


def test_none_selection_keeps_disappearance_marker_during_handoff(
    qt_app: QApplication,
) -> None:
    listing = QListWidget()
    details = QPlainTextEdit()
    listing.setProperty("pathenaSelectionDisappeared", "old-claim-id")
    details.setProperty("pathenaSelectionDisappeared", "old-claim-id")

    KnowledgeSelectionContinuity._clear_disappearance_on_new_selection(
        _ContinuityStub(details),  # type: ignore[arg-type]
        listing,
        None,
    )

    assert listing.property("pathenaSelectionDisappeared") == "old-claim-id"
    assert details.property("pathenaSelectionDisappeared") == "old-claim-id"
