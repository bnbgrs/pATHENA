from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from athena.desktop.pathena_pallas_field import PallasSelection, PallasSemanticField
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticNode,
)


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


def _node(node_id: str, kind: PallasNodeKind, title: str) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=node_id,
        kind=kind,
        entity_type=kind.value,
        entity_id=node_id,
        revision_id=None,
        title=title,
        summary=f"Summary for {title}",
        epistemic_status="verified",
        cited=True,
    )


def _snapshot() -> PallasGraphSnapshot:
    nodes = (
        _node("focus", PallasNodeKind.FOCUS, "Grounded response"),
        _node("claim", PallasNodeKind.CLAIM, "Claim"),
        _node("source", PallasNodeKind.SOURCE, "Source"),
    )
    return PallasGraphSnapshot(
        graph_id="graph:test",
        nodes=nodes,
        edges=(),
        focus_id="focus",
        status="ready",
        status_detail="Three grounded semantic nodes.",
    )


def _ready_field(qapp: QApplication, *, compact: bool = False) -> PallasSemanticField:
    field = PallasSemanticField()
    field.set_compact_mode(compact)
    field.resize(640, 420)
    field.show()
    field.set_snapshot(_snapshot())
    qapp.processEvents()
    field.canvas.setFocus()
    return field


def test_arrow_focus_is_deterministic_and_does_not_select_until_activation(
    qapp: QApplication,
) -> None:
    field = _ready_field(qapp)
    try:
        assert field.property("pathenaPallasSelectionId") == "focus"

        QTest.keyClick(field.canvas, Qt.Key.Key_Right)
        qapp.processEvents()
        focused = field._focused_item()
        assert focused is not None
        assert focused.node.node_id == "claim"
        assert field.property("pathenaPallasSelectionId") == "focus"

        QTest.keyClick(field.canvas, Qt.Key.Key_Return)
        qapp.processEvents()
        assert field.property("pathenaPallasSelectionId") == "claim"
    finally:
        field.close()
        field.deleteLater()


def test_escape_clears_selection_without_destroying_keyboard_focus(
    qapp: QApplication,
) -> None:
    field = _ready_field(qapp)
    emissions: list[object] = []
    field.selection_changed.connect(emissions.append)
    try:
        QTest.keyClick(field.canvas, Qt.Key.Key_Right)
        QTest.keyClick(field.canvas, Qt.Key.Key_Space)
        qapp.processEvents()
        focused_before = field._focused_item()
        assert focused_before is not None
        assert isinstance(emissions[-1], PallasSelection)

        QTest.keyClick(field.canvas, Qt.Key.Key_Escape)
        qapp.processEvents()
        focused_after = field._focused_item()
        assert field.property("pathenaPallasSelectionId") == ""
        assert emissions[-1] is None
        assert focused_after is focused_before
    finally:
        field.close()
        field.deleteLater()


def test_arrow_navigation_stops_at_graph_boundaries_instead_of_wrapping(
    qapp: QApplication,
) -> None:
    field = _ready_field(qapp)
    try:
        for _ in range(6):
            QTest.keyClick(field.canvas, Qt.Key.Key_Right)
        qapp.processEvents()
        focused = field._focused_item()
        assert focused is not None
        assert focused.node.node_id == "source"

        for _ in range(6):
            QTest.keyClick(field.canvas, Qt.Key.Key_Left)
        qapp.processEvents()
        focused = field._focused_item()
        assert focused is not None
        assert focused.node.node_id == "focus"
    finally:
        field.close()
        field.deleteLater()


def test_compact_and_full_fields_share_keyboard_selection_semantics(
    qapp: QApplication,
) -> None:
    full = _ready_field(qapp, compact=False)
    compact = _ready_field(qapp, compact=True)
    try:
        for field in (full, compact):
            QTest.keyClick(field.canvas, Qt.Key.Key_Right)
            QTest.keyClick(field.canvas, Qt.Key.Key_Space)
            qapp.processEvents()
            assert field.property("pathenaPallasSelectionId") == "claim"
            assert "arrow keys" in field.canvas.accessibleDescription().casefold()
    finally:
        for field in (full, compact):
            field.close()
            field.deleteLater()
