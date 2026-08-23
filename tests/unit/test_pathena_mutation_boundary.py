from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPlainTextEdit, QPushButton, QWidget

from athena.desktop.pathena_mutation_boundary_5800 import (
    BoundaryTarget,
    MutationBoundaryController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_read_only_detail_remains_read_only_and_non_mutating() -> None:
    _app()
    window = QWidget()
    detail = QPlainTextEdit(window)
    detail.setReadOnly(True)
    target = BoundaryTarget(
        None,
        None,
        None,
        "Job details",
        "read-only",
        "Inspects durable job state.",
    )

    controller = MutationBoundaryController(window)
    controller.register(detail, target)

    assert detail.isReadOnly() is True
    assert detail.property("pathenaInteractionBoundary") == "read-only"
    assert detail.property("pathenaMutationCapable") is False
    assert detail.property("pathenaVerifiedReadOnly") is True


def test_mutation_button_preserves_existing_action_role_and_enablement() -> None:
    _app()
    window = QWidget()
    button = QPushButton("CANCEL", window)
    button.setEnabled(False)
    button.setProperty("pathenaActionRole", "destructive")
    target = BoundaryTarget(
        None,
        None,
        None,
        "Cancel job",
        "mutation",
        "Persists cancellation for the selected job.",
    )

    controller = MutationBoundaryController(window)
    controller.register(button, target)

    assert button.isEnabled() is False
    assert button.property("pathenaMutationCapable") is True
    assert button.property("pathenaBoundaryActionRole") == "destructive"


def test_boundary_suffix_is_not_duplicated_after_resync() -> None:
    _app()
    window = QWidget()
    button = QPushButton("HISTORY", window)
    button.setToolTip("Load history")
    target = BoundaryTarget(
        None,
        None,
        None,
        "Knowledge history",
        "inspection-action",
        "Loads immutable revision history for inspection.",
    )

    controller = MutationBoundaryController(window)
    controller.register(button, target)
    controller._sync(button)

    assert button.toolTip().count("Interaction boundary:") == 1
    assert button.accessibleDescription().count("Interaction boundary:") == 1


def test_controller_does_not_turn_editable_surface_read_only() -> None:
    _app()
    window = QWidget()
    detail = QPlainTextEdit(window)
    detail.setReadOnly(False)
    target = BoundaryTarget(
        None,
        None,
        None,
        "Diagnostic surface",
        "read-only",
        "Presentation metadata only.",
    )

    controller = MutationBoundaryController(window)
    controller.register(detail, target)

    assert detail.isReadOnly() is False
    assert detail.property("pathenaVerifiedReadOnly") is False
