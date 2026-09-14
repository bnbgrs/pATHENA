from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QGraphicsSimpleTextItem, QWidget
from shiboken6 import delete

from athena.desktop.pathena_pallas_field import PallasGroundedFieldController
from athena.desktop.pathena_pallas_living_qt import PallasLivingQtController
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


def _snapshot_with_every_kind() -> PallasGraphSnapshot:
    nodes = tuple(
        PallasSemanticNode(
            node_id=f"node:{kind.value}",
            kind=kind,
            entity_type="canonical_claim",
            entity_id=f"entity:{kind.value}",
            revision_id=f"revision:{kind.value}",
            title=kind.value,
            summary=f"Grounded {kind.value} node",
            epistemic_status="supported",
            cited=True,
            confidence=0.9,
        )
        for kind in PallasNodeKind
    )
    return PallasGraphSnapshot(
        graph_id="graph:canonical-glyph-contract",
        nodes=nodes,
        edges=(),
        focus_id="node:focus",
        status="ready",
        status_detail="Every canonical PALLAS node kind.",
    )


def _visible_glyphs(controller: PallasGroundedFieldController, node_id: str) -> set[str]:
    item = controller.field._items[node_id]  # noqa: SLF001
    return {
        child.text()
        for child in item.childItems()
        if isinstance(child, QGraphicsSimpleTextItem)
    }


def test_living_semantic_lens_preserves_every_canonical_node_glyph(
    qapp: QApplication,
) -> None:
    window = QWidget()
    placeholder = QWidget(window)
    placeholder.setObjectName("pallasVisualPlaceholder")
    grounded = PallasGroundedFieldController(window, None)
    snapshot = _snapshot_with_every_kind()
    grounded.apply_snapshot(snapshot)

    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001 - deterministic presentation regression
    try:
        living._tick()  # noqa: SLF001
        qapp.processEvents()

        for node in snapshot.nodes:
            assert node.glyph in _visible_glyphs(grounded, node.node_id)

        living.set_lens("age")
        living.set_lens("vitality")
        living.set_lens("semantic")
        qapp.processEvents()

        for node in snapshot.nodes:
            assert node.glyph in _visible_glyphs(grounded, node.node_id)
        assert grounded.field.snapshot is snapshot
    finally:
        living.stop()
        delete(window)
