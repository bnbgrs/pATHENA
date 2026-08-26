from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid

from athena.desktop.app import create_application
from athena.desktop.pathena_pallas_field import (
    PallasGroundedFieldController,
    PallasSelection,
    install_pallas_grounded_field,
)
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticEdge,
    PallasSemanticNode,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-pallas-synchronized-workspace-test"])


def _snapshot() -> PallasGraphSnapshot:
    focus = PallasSemanticNode(
        node_id="focus:run-1",
        kind=PallasNodeKind.FOCUS,
        entity_type="grounded_processing_run",
        entity_id="run-1",
        revision_id=None,
        title="Grounded response",
        summary="A real grounded response.",
        epistemic_status=None,
        cited=True,
    )
    claim = PallasSemanticNode(
        node_id="canonical_claim:claim-1",
        kind=PallasNodeKind.CLAIM,
        entity_type="canonical_claim",
        entity_id="claim-1",
        revision_id="revision-1",
        title="Supported claim",
        summary="A persisted claim with evidence.",
        epistemic_status="supported",
        cited=True,
        confidence=0.92,
    )
    return PallasGraphSnapshot(
        graph_id="grounded-run:run-1",
        nodes=(focus, claim),
        edges=(PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),),
        focus_id=focus.node_id,
        status="ready",
        status_detail="One real claim from grounded run run-1.",
    )


def _surface() -> tuple[QApplication, PathenaMainWindow, PallasGroundedFieldController]:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_pallas_grounded_field(window)
    window.resize(1480, 900)
    window.show()
    app.processEvents()
    return app, window, controller


def test_workspace_created_after_snapshot_receives_same_graph_and_focus() -> None:
    app, window, controller = _surface()
    controller.apply_snapshot(_snapshot())

    workspace = controller.create_workspace(window)
    app.processEvents()

    assert workspace.field.snapshot == controller.field.snapshot
    assert workspace.field.property("pathenaPallasMode") == "full"
    assert workspace.field.property("pathenaPallasSelectionId") == "focus:run-1"
    assert workspace.breadcrumb.text().endswith("FOCUS / Grounded response")
    window.close()


def test_selection_in_full_view_updates_compact_view_and_inspector_contract() -> None:
    app, window, controller = _surface()
    selections: list[object] = []
    controller.selection_changed.connect(selections.append)
    controller.apply_snapshot(_snapshot())
    workspace = controller.create_workspace(window)

    assert workspace.field.focus_node("canonical_claim:claim-1")
    app.processEvents()

    assert controller.field.property("pathenaPallasSelectionId") == (
        "canonical_claim:claim-1"
    )
    assert isinstance(selections[-1], PallasSelection)
    assert selections[-1].node.entity_id == "claim-1"
    assert workspace.breadcrumb.text().endswith("CLAIM / Supported claim")
    window.close()


def test_clear_selection_is_synchronized_without_stale_context() -> None:
    app, window, controller = _surface()
    controller.apply_snapshot(_snapshot())
    workspace = controller.create_workspace(window)
    workspace.field.focus_node("canonical_claim:claim-1")

    workspace.field.clear_selection()
    app.processEvents()

    assert controller.field.property("pathenaPallasSelectionId") == ""
    assert workspace.field.property("pathenaPallasSelectionId") == ""
    assert workspace.breadcrumb.text() == "PALLAS / grounded-run:run-1"
    window.close()


def test_loading_error_and_empty_states_reach_all_views_without_fake_nodes() -> None:
    _app_instance, window, controller = _surface()
    workspace = controller.create_workspace(window)

    window.ground_button.setChecked(True)
    controller.apply_chat_busy(True)
    assert controller.field.property("pathenaUiState") == "loading"
    assert workspace.field.property("pathenaUiState") == "loading"
    assert workspace.field.snapshot is None

    controller.apply_chat_operation_failure("send_grounded", "Provider unavailable")
    assert controller.field.property("pathenaUiState") == "error"
    assert workspace.field.property("pathenaUiState") == "error"
    assert "Provider unavailable" in workspace.field.state_label.text()
    assert workspace.field.scene.items() == []
    window.close()


def test_destroyed_full_workspace_is_removed_without_late_signal_failure() -> None:
    app, window, controller = _surface()
    workspace = controller.create_workspace()
    field = workspace.field
    workspace.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    assert not isValid(workspace)
    assert not isValid(field)
    assert controller._live_workspaces() == ()
    controller._set_state("error", "Core disconnected")
    window.close()
