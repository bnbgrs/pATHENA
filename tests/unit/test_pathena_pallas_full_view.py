from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

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


def test_open_workspace_reuses_one_synchronized_full_surface() -> None:
    app, window, grounded, full_view = _surface()
    grounded.apply_snapshot(_snapshot())

    full_view.open_workspace()
    app.processEvents()
    first_workspace = full_view.workspace
    first_host = window.findChild(QFrame, "pallasShellWorkspaceHost")
    conversation = window.findChild(QFrame, "conversation")

    assert full_view.dialog is None
    assert full_view.is_open
    assert first_workspace is not None and first_workspace.isVisible()
    assert first_host is not None and first_host.isVisible()
    assert first_host.property("pathenaPallasShellHosted") is True
    assert first_workspace.property("pathenaPallasShellHosted") is True
    back_button = window.findChild(QPushButton, "pallasBackButton")
    fit_button = window.findChild(QPushButton, "pallasFitButton")
    legend = window.findChild(QLabel, "pallasSemanticLegend")
    assert back_button is not None and back_button.isVisible()
    assert back_button.accessibleName() == "Back to current workspace"
    vitality_button = window.findChild(QPushButton, "pallasLensVitalityButton")
    age_button = window.findChild(QPushButton, "pallasLensAgeButton")
    assert fit_button is not None and fit_button.isVisible()
    assert fit_button.accessibleName() == "Fit all PALLAS nodes"
    assert vitality_button is not None
    assert "not epistemic confidence" in vitality_button.toolTip()
    assert age_button is not None
    assert "not source or document age" in age_button.toolTip()
    assert legend is not None and legend.isVisible()
    assert "◉ FOCUS" in legend.text()
    assert "△ SOURCE" in legend.text()
    assert "× CONFLICT" in legend.text()
    assert first_workspace.field.property("pathenaPallasMode") == "full"
    assert first_workspace.field.snapshot == grounded.field.snapshot
    assert window.property("pathenaPallasShellOpen") is True
    assert conversation is not None and not conversation.isVisible()

    full_view.close_workspace()
    app.processEvents()
    assert not full_view.is_open
    assert not first_host.isVisible()
    assert conversation.isVisible()

    full_view.open_workspace()
    app.processEvents()

    assert full_view.dialog is None
    assert full_view.workspace is first_workspace
    assert window.findChild(QFrame, "pallasShellWorkspaceHost") is first_host
    assert first_host.isVisible()
    assert first_workspace.isVisible()
    assert full_view.is_open
    full_view.dispose()
    window.close()


def test_double_click_on_compact_canvas_opens_full_pallas() -> None:
    app, window, grounded, full_view = _surface()

    QTest.mouseDClick(
        grounded.field.canvas.viewport(),
        Qt.MouseButton.LeftButton,
    )
    app.processEvents()

    workspace = full_view.workspace
    host = window.findChild(QFrame, "pallasShellWorkspaceHost")
    assert full_view.dialog is None
    assert full_view.is_open
    assert workspace is not None and workspace.isVisible()
    assert host is not None and host.isVisible()
    assert window.property("pathenaPallasShellOpen") is True
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
    assert workspace.breadcrumb.text().endswith("CLAIM / Supported claim")

    inspector.dispose()
    full_view.dispose()
    window.close()


def test_full_view_reclaims_stale_inspector_and_restores_previous_context() -> None:
    app, window, grounded, full_view = _surface()
    object_id = window.findChild(QLabel, "objectId")
    heading = window.findChild(QLabel, "inspectorHeading")
    body = window.findChild(QLabel, "inspectorBody")
    panel = window.findChild(QFrame, "inspector")
    assert object_id is not None
    assert heading is not None
    assert body is not None
    assert panel is not None

    object_id.setText("SOURCE / NONE")
    heading.setText("No source selected")
    body.setText("Source workspace context")
    panel.show()

    inspector = install_pallas_context_inspector(window, grounded)
    grounded.apply_snapshot(_snapshot())
    app.processEvents()
    assert panel.property("pathenaPallasSelectionId") == "focus:run-2"

    object_id.setText("SOURCE / NONE")
    heading.setText("No source selected")
    body.setText("Stale source context")

    full_view.open_workspace()
    app.processEvents()
    assert object_id.text().startswith("PALLAS / FOCUS /")
    assert heading.text().endswith("Grounded response")
    assert panel.property("pathenaPallasSelectionId") == "focus:run-2"

    full_view.close_workspace()
    app.processEvents()
    assert object_id.text() == "SOURCE / NONE"
    assert heading.text() == "No source selected"
    assert body.text() == "Source workspace context"
    assert panel.property("pathenaPallasSelectionId") is None

    inspector.dispose()
    full_view.dispose()
    window.close()



def test_full_view_uses_dedicated_v3_inspector_without_exposing_legacy_panel() -> None:
    app, window, grounded, full_view = _surface()
    inspector = install_pallas_context_inspector(window, grounded)
    grounded.apply_snapshot(_snapshot())

    full_view.open_workspace()
    app.processEvents()

    legacy_panel = window.findChild(QFrame, "inspector")
    v3_panel = window.findChild(QFrame, "v3PallasInspector")
    v3_title = window.findChild(QLabel, "v3PallasInspectorTitle")
    v3_body = window.findChild(QLabel, "v3PallasInspectorBody")
    assert legacy_panel is not None
    assert v3_panel is not None and v3_panel.isVisible()
    assert not legacy_panel.isVisible()
    assert v3_title is not None and v3_title.text().endswith("Grounded response")
    assert v3_body is not None and "Graph  grounded-run:run-2" in v3_body.text()
    assert "Relationships  1" in v3_body.text()
    assert "→ cites · ◆ Supported claim" in v3_body.text()

    workspace = full_view.workspace
    assert workspace is not None
    assert workspace.field.focus_node("canonical_claim:claim-2")
    app.processEvents()

    assert v3_title.text().endswith("Supported claim")
    assert "Confidence  0.91" in v3_body.text()
    assert "Relationships  1" in v3_body.text()
    assert "← cites · ◉ Grounded response" in v3_body.text()
    assert legacy_panel.property("pathenaPallasSelectionId") == "canonical_claim:claim-2"
    assert not legacy_panel.isVisible()

    full_view.close_workspace()
    app.processEvents()
    inspector.dispose()
    full_view.dispose()
    window.close()


def test_living_cadence_tracks_compact_and_full_workspace_visibility() -> None:
    app, window, grounded, full_view = _surface()
    grounded.apply_snapshot(_snapshot())
    living = full_view.living_controller
    living._timer.stop()  # noqa: SLF001 - deterministic cadence regression
    try:
        living._tick()  # noqa: SLF001
        app.processEvents()

        expected_idle_interval = (
            living._compact_interval_ms  # noqa: SLF001
            if grounded.field.isVisible()
            else living._idle_interval_ms  # noqa: SLF001
        )
        expected_idle_fps = round(1000 / expected_idle_interval)
        assert living._timer.interval() == expected_idle_interval  # noqa: SLF001
        assert grounded.field.property("pathenaPallasTargetFps") == expected_idle_fps

        full_view.open_workspace()
        app.processEvents()
        living._tick()  # noqa: SLF001
        app.processEvents()

        workspace = full_view.workspace
        status = window.findChild(QLabel, "pallasLivingStatus")
        assert workspace is not None
        assert living._timer.interval() == living._active_interval_ms  # noqa: SLF001
        assert workspace.field.property("pathenaPallasTargetFps") == 30
        assert status is not None
        assert "30 FPS" in status.text()
        assert "explicit edges" in status.toolTip()
        assert "presentation signals" in status.accessibleDescription()
        assert id(workspace.field) in living._bindings  # noqa: SLF001

        full_view.close_workspace()
        app.processEvents()
        living._tick()  # noqa: SLF001
        app.processEvents()

        assert id(workspace.field) not in living._bindings  # noqa: SLF001
        if grounded.field.isVisible():
            assert id(grounded.field) in living._bindings  # noqa: SLF001
    finally:
        full_view.dispose()
        window.close()


def test_relationship_cache_refreshes_for_same_graph_id_content_change() -> None:
    app, window, grounded, full_view = _surface()
    grounded.apply_snapshot(_snapshot())
    full_view.open_workspace()
    workspace = full_view.workspace
    body = window.findChild(QLabel, "v3PallasInspectorBody")
    assert workspace is not None
    assert body is not None

    assert workspace.field.focus_node("canonical_claim:claim-2")
    app.processEvents()
    assert "Relationships  1" in body.text()

    focus, claim = _snapshot().nodes
    knowledge = PallasSemanticNode(
        node_id="knowledge:unit-1",
        kind=PallasNodeKind.KNOWLEDGE,
        entity_type="knowledge_unit",
        entity_id="unit-1",
        revision_id="revision-unit-1",
        title="Accepted knowledge",
        summary="A durable knowledge unit.",
        epistemic_status="accepted",
        cited=False,
    )
    updated = PallasGraphSnapshot(
        graph_id="grounded-run:run-2",
        nodes=(focus, claim, knowledge),
        edges=(
            PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),
            PallasSemanticEdge(claim.node_id, knowledge.node_id, "supports"),
        ),
        focus_id=focus.node_id,
        status="ready",
        status_detail="Claim plus one explicit knowledge relationship.",
    )
    grounded.apply_snapshot(updated)
    assert workspace.field.focus_node("canonical_claim:claim-2")
    app.processEvents()

    assert "Relationships  2" in body.text()
    assert "→ supports · ■ Accepted knowledge" in body.text()

    full_view.dispose()
    window.close()

def test_full_view_status_tracks_nonready_grounded_state() -> None:
    app, window, grounded, full_view = _surface()
    grounded.apply_snapshot(_snapshot())
    full_view.open_workspace()
    living = full_view.living_controller
    living._timer.stop()  # noqa: SLF001
    try:
        living._tick()  # noqa: SLF001
        app.processEvents()
        status = window.findChild(QLabel, "pallasLivingStatus")
        assert status is not None
        assert "ACTIVE" in status.text()

        empty = PallasGraphSnapshot(
            graph_id="grounded-run:empty",
            nodes=(),
            edges=(),
            focus_id=None,
            status="empty",
            status_detail="No grounded context is available.",
        )
        grounded.apply_snapshot(empty)
        living._tick()  # noqa: SLF001
        app.processEvents()

        assert status.text() == "FIELD • NO GROUNDED CONTEXT"
        assert "idle until a ready grounded graph" in status.toolTip()
    finally:
        full_view.dispose()
        window.close()

