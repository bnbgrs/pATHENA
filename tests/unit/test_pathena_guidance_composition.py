from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_guidance_composition_6100 import GuidanceCompositionController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QWidget, QWidget, GuidanceCompositionController]:
    window = QWidget()
    surface = QWidget(window)
    surface.setAccessibleDescription("Base assistive description")
    surface.setToolTip("Base tooltip\nKeyboard: Space activates.")
    surface.setProperty("pathenaComposerBlockingReason", "Chat is busy.")
    surface.setProperty("pathenaComposerRecoveryCondition", "Wait for completion.")
    surface.setProperty("pathenaEnablementReason", "Unavailable while busy.")
    surface.setProperty("pathenaEnablementRestoreCondition", "Wait for completion.")
    surface.setProperty("pathenaBoundaryExplanation", "This action mutates durable state.")
    surface.setProperty("pathenaCancellationPhase", "requested")
    surface.setProperty("pathenaCancellationSelectedState", "cancel_requested")
    controller = GuidanceCompositionController(window)
    controller.register(surface, "Cancel job")
    return window, surface, controller


def test_tooltip_preserves_static_lines_and_limits_dynamic_overlays() -> None:
    _app()
    _window, surface, _controller = _surface()

    tooltip = surface.toolTip()
    assert tooltip.startswith("Base tooltip\nKeyboard: Space activates.")
    assert surface.property("pathenaGuidanceTooltipOverlayCount") == 2
    assert "Readiness:" in tooltip
    assert "Cancellation:" in tooltip
    assert "Interaction boundary:" not in tooltip


def test_accessible_description_keeps_all_distinct_guidance() -> None:
    _app()
    _window, surface, _controller = _surface()

    description = surface.accessibleDescription()
    assert "Base assistive description" in description
    assert "Chat is busy" in description
    assert "terminal cancellation is still pending" in description
    assert "Unavailable while busy" in description
    assert "mutates durable state" in description


def test_later_accessible_state_update_recomposes_other_guidance() -> None:
    app = _app()
    _window, surface, _controller = _surface()

    surface.setAccessibleDescription("New semantic state description")
    surface.setProperty("pathenaAccessibleUiState", "error")
    app.processEvents()
    app.processEvents()

    description = surface.accessibleDescription()
    assert description.startswith("New semantic state description")
    assert "Chat is busy" in description
    assert "terminal cancellation is still pending" in description
    assert "mutates durable state" in description


def test_recomposition_does_not_duplicate_dynamic_sections() -> None:
    app = _app()
    _window, surface, controller = _surface()

    surface.setProperty("pathenaComposerRecoveryCondition", "Wait for the current operation.")
    app.processEvents()
    app.processEvents()
    controller._compose(surface, refresh_base=True)

    tooltip = surface.toolTip()
    assert tooltip.count("Readiness:") == 1
    assert tooltip.count("Cancellation:") == 1
