from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_detail_provenance_6300 import DetailProvenanceController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_retained_content_is_labeled_while_new_selection_loads() -> None:
    mode, text, rendered = DetailProvenanceController._presentation(
        label="Source",
        selected="source-new",
        rendered="source-old",
        state="busy",
        has_content=True,
    )

    assert mode == "retained"
    assert text == "RETAINED · source-old · loading source-new"
    assert rendered == "source-old"


def test_success_marks_selected_identity_as_current() -> None:
    mode, text, rendered = DetailProvenanceController._presentation(
        label="Knowledge",
        selected="knowledge-2",
        rendered="knowledge-1",
        state="success",
        has_content=True,
    )

    assert mode == "current"
    assert text == "CURRENT · knowledge-2"
    assert rendered == "knowledge-2"


def test_failed_load_does_not_relabel_retained_content_as_current() -> None:
    mode, text, rendered = DetailProvenanceController._presentation(
        label="Claim",
        selected="claim-new",
        rendered="claim-old",
        state="error",
        has_content=True,
    )

    assert mode == "retained-error"
    assert text == "RETAINED · claim-old · load failed for claim-new"
    assert rendered == "claim-old"


def test_controller_inserts_quiet_provenance_before_detail_pane() -> None:
    app = _app()
    window = QWidget()
    parent = QWidget(window)
    layout = QVBoxLayout(parent)
    listing = QListWidget(parent)
    detail = QPlainTextEdit(parent)
    detail.setPlainText("Existing detail")
    item = QListWidgetItem("Item")
    item.setData(Qt.ItemDataRole.UserRole, "entity-1")
    listing.addItem(item)
    listing.setCurrentItem(item)
    layout.addWidget(listing)
    layout.addWidget(detail)
    window.show()
    app.processEvents()

    controller = DetailProvenanceController(window)
    controller.register(listing, detail, "Entity")
    app.processEvents()

    provenance = parent.findChild(QWidget, "pathenaDetailProvenance")
    assert provenance is not None
    assert detail.property("pathenaDetailContentIdentity") == "entity-1"
    assert detail.property("pathenaDetailProvenanceMode") == "current"
