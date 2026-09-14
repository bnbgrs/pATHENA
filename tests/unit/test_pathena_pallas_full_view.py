from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.app import create_application
from athena.desktop.pathena_pallas_field import install_pallas_grounded_field
from athena.desktop.pathena_pallas_full_view import install_pallas_full_view
from athena.desktop.pathena_pallas_inspector import install_pallas_context_inspector
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticEdge,
    PallasSemanticNode,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-pallas-full-view-test"])


def _snapshot() -> PallasGraphSnapshot:
    focus = PallasSemanticNode(
        node_id="focus:run-2",
        kind=PallasNodeKind.FOCUS,
        entity_type="grounded_processing_run",
        entity_id="run-2",
        revision_id=None,
        title="Grounded response",
        summary="A grounded response for the synchronized full view.",
        epistemic_status=None,
        cited=True,
    )
    claim = PallasSemanticNode(
        node_id="canonical_claim:claim-2",
        kind=PallasNodeKind.CLAIM,
        entity_type="canonical_claim",
        entity_id="claim-2",
        revision_id="revision-2",
        title="Supported claim",
        summary="A persisted claim with evidence.",
        epistemic_status="supported",
        cited=True,
        confidence=0.91,
    )
    return PallasGraphSnapshot(
        graph_id="grounded-run:run-2",
        nodes=(focus, claim),
        edges=(PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),),
        focus_id=focus.node_id,
        status="ready",
        status_detail="One real claim from grounded run run-2.",
    )


def _surface():
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    grounded = install_pallas_grounded_field(window)
    full_view = install_pallas_full_view(window, grounded)
    window.resize(1480, 900)
    window.show()
    app.processEvents()
    return app, window, grounded, full_view


def test_open_workspace_reuses_one_synchronized_shell_surface() -> None:
    app, window, grounded, full_view = _surface()
    grounded.apply_snapshot(_snapshot())
    center = window.findChild(QFrame, "conversation")
    assert center is not None and center.isVisible()

    full_view.open_workspace()
    app.processEvents()
    first_workspace = full_view.workspace

    assert full_view.dialog is None
    assert first_workspace is not None and first_workspace.isVisible()
    assert first_workspace.objectName() == "pallasShellWorkspace"
    assert first_workspace.property("pathenaPallasShellHosted") is True
    assert first_workspace.field.property("pathenaPallasMode") == "full"
    assert first_workspace.field.snapshot == grounded.field.snapshot
    assert full_view.is_open
    assert window.property("pathenaPallasShellOpen") is True
    assert not center.isVisible()
    assert window.findChild(QFrame, "referenceBody") is not None

    full_view.close_workspace()
    app.processEvents()
    assert not first_workspace.isVisible()
    assert center.isVisible()

    full_view.open_workspace()
    app.processEvents()
    assert full_view.workspace is first_workspace
    assert first_workspace.isVisible()
    assert not center.isVisible()
    full_view.dispose()
    window.close()


def test_primary_navigation_restores_routed_workspace_from_pallas() -> None:
    app, window, _grounded, full_view = _surface()
    full_view.open_workspace()
    app.processEvents()
    workspace = full_view.workspace
    center = window.findChild(QFrame, "conversation")
    assert workspace is not None and workspace.isVisible()
    assert center is not None and not center.isVisible()
    assert window.navigation.count() == 7
    assert window.pages.count() == 7

    window.navigation.setCurrentRow(1)
    app.processEvents()

    assert window.pages.currentIndex() == 1
    assert not full_view.is_open
    assert not workspace.isVisible()
    assert center.isVisible()
    full_view.dispose()
    window.close()


def test_double_click_on_compact_canvas_opens_full_pallas_in_shell() -> None:
    app, window, grounded, full_view = _surface()

    QTest.mouseDClick(
        grounded.field.canvas.viewport(),
        Qt.MouseButton.LeftButton,
    )
    app.processEvents()

    assert full_view.workspace is not None
    assert full_view.workspace.isVisible()
    assert full_view.is_open
    assert window.isVisible()
    assert "double-click" in grounded.target.toolTip().casefold()
    full_view.dispose()
    window.close()


def test_full_view_selection_updates_compact_view_and_shared_inspector() -> None:
    app, window, grounded, full_view = _surface()
    inspector = install_pallas_context_inspector(window, grounded)
    grounded.apply_snapshot(_snapshot())
    full_view.open_workspace()
    workspace = full_view.workspace
    assert workspace is not None

    assert workspace.field.focus_node("canonical_claim:claim-2")
    app.processEvents()

    assert grounded.field.property("pathenaPallasSelectionId") == "canonical_claim:claim-2"
    panel = window.findChild(QFrame, "inspector")
    assert panel is not None
    assert panel.property("pathenaPallasSelectionId") == "canonical_claim:claim-2"
    assert panel.isVisible()
    assert workspace.breadcrumb.text().endswith("CLAIM / Supported claim")

    inspector.dispose()
    full_view.dispose()
    window.close()
