from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

from athena.desktop.app import create_application
from athena.desktop.pathena_pallas_field import install_pallas_grounded_field
from athena.desktop.pathena_pallas_full_view import install_pallas_full_view
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticEdge,
    PallasSemanticNode,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-pallas-living-shell-test"])


def _snapshot() -> PallasGraphSnapshot:
    focus = PallasSemanticNode(
        node_id="focus:living-shell",
        kind=PallasNodeKind.FOCUS,
        entity_type="grounded_processing_run",
        entity_id="living-shell",
        revision_id=None,
        title="Grounded response",
        summary="A grounded response driving the living shell field.",
        epistemic_status=None,
        cited=True,
    )
    claim = PallasSemanticNode(
        node_id="canonical_claim:living-shell",
        kind=PallasNodeKind.CLAIM,
        entity_type="canonical_claim",
        entity_id="living-shell-claim",
        revision_id="living-shell-revision",
        title="Supported living claim",
        summary="A persisted claim with grounded evidence.",
        epistemic_status="supported",
        cited=True,
        confidence=0.94,
    )
    return PallasGraphSnapshot(
        graph_id="grounded-run:living-shell",
        nodes=(focus, claim),
        edges=(PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),),
        focus_id=focus.node_id,
        status="ready",
        status_detail="Two grounded nodes for living shell integration.",
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


def test_shell_hosted_living_view_shares_graph_and_switches_lenses() -> None:
    app, window, grounded, full_view = _surface()
    snapshot = _snapshot()
    grounded.apply_snapshot(snapshot)

    full_view.open_workspace()
    app.processEvents()
    full_view.living_controller._tick()  # noqa: SLF001
    app.processEvents()

    workspace = full_view.workspace
    host = window.findChild(QFrame, "pallasShellWorkspaceHost")
    status = window.findChild(QLabel, "pallasLivingStatus")
    age = window.findChild(QPushButton, "pallasLensAgeButton")
    vitality = window.findChild(QPushButton, "pallasLensVitalityButton")

    assert full_view.dialog is None
    assert workspace is not None and workspace.isVisible()
    assert host is not None and host.isVisible()
    assert host.property("pathenaPallasShellHosted") is True
    assert workspace.property("pathenaPallasShellHosted") is True
    assert grounded.field.snapshot == snapshot
    assert workspace.field.snapshot == snapshot
    assert full_view.living_controller.engine.snapshot == snapshot
    assert grounded.field.property("pathenaPallasLiving") is True
    assert workspace.field.property("pathenaPallasLiving") is True
    assert full_view.living_controller.lens == "semantic"

    assert age is not None
    age.click()
    app.processEvents()
    assert full_view.living_controller.lens == "age"
    assert grounded.field.property("pathenaPallasLens") == "age"
    assert workspace.field.property("pathenaPallasLens") == "age"

    assert vitality is not None
    vitality.click()
    full_view.living_controller._tick()  # noqa: SLF001
    app.processEvents()
    assert full_view.living_controller.lens == "vitality"
    assert grounded.field.property("pathenaPallasLens") == "vitality"
    assert workspace.field.property("pathenaPallasLens") == "vitality"
    assert status is not None and "VITALITY" in status.text()
    assert grounded.field.snapshot == snapshot
    assert workspace.field.snapshot == snapshot

    full_view.dispose()
    assert full_view.living_controller.engine.snapshot is None
    window.close()


def test_unknown_lens_fails_closed_without_leaving_shell_workspace() -> None:
    app, window, grounded, full_view = _surface()
    snapshot = _snapshot()
    grounded.apply_snapshot(snapshot)
    full_view.open_workspace()
    full_view.living_controller._tick()  # noqa: SLF001
    app.processEvents()

    workspace = full_view.workspace
    assert workspace is not None and workspace.isVisible()

    with pytest.raises(ValueError, match="Unsupported PALLAS lens"):
        full_view.living_controller.set_lens("confidence")

    assert full_view.is_open
    assert workspace.isVisible()
    assert full_view.living_controller.lens == "semantic"
    assert grounded.field.snapshot == snapshot
    assert workspace.field.snapshot == snapshot

    full_view.dispose()
    window.close()
