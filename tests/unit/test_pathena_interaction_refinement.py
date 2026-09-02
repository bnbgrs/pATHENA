from __future__ import annotations

from PySide6.QtWidgets import QApplication

from athena.desktop import pathena_interaction_refinement as refinement
from athena.desktop.app import create_application
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-interaction-refinement-test"])


def test_interaction_refinement_uses_short_lightweight_motion() -> None:
    assert refinement._ANIMATION_MS == 140
    assert refinement._COMPACT_WIDTH < refinement._COMFORTABLE_WIDTH


def test_interaction_refinement_honours_explicit_reduced_motion(monkeypatch) -> None:
    monkeypatch.setenv("PATHENA_REDUCED_MOTION", "1")

    assert refinement._resolved_animation_duration() == 0


def test_interaction_refinement_keeps_normal_motion_bounded(monkeypatch) -> None:
    monkeypatch.delenv("PATHENA_REDUCED_MOTION", raising=False)
    monkeypatch.delenv("QT_QUICK_CONTROLS_REDUCE_MOTION", raising=False)

    assert refinement._resolved_animation_duration() == 140


def test_reduced_motion_disclosure_changes_geometry_immediately(monkeypatch) -> None:
    monkeypatch.setenv("PATHENA_REDUCED_MOTION", "1")
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = refinement.install_interaction_refinement(window)
    window.show()
    try:
        evidence = window.evidence_chain
        window._set_context_available(True)
        app.processEvents()

        window.context_button.click()
        assert controller._animation_ms == 0
        assert evidence.isHidden() is False
        assert evidence.maximumHeight() > 0

        window.context_button.click()
        assert evidence.isHidden()
        assert evidence.maximumHeight() == 0
    finally:
        window.close()
        app.processEvents()


def test_interaction_refinement_keeps_responsive_breakpoints_explicit() -> None:
    assert refinement._COMPACT_WIDTH == 1260
    assert refinement._COMFORTABLE_WIDTH == 1500


def test_interaction_refinement_is_presentation_only_by_contract() -> None:
    source = refinement.__doc__ or ""
    assert "presentation-only" in source
    assert "domain" in source
    assert "persistence" in source
    assert "scheduler" in source
    assert "API" in source


def test_interaction_refinement_animates_only_geometry_properties() -> None:
    names = refinement.PathenaInteractionRefinement._animate_inspector.__code__.co_consts
    evidence_names = refinement.PathenaInteractionRefinement._animate_evidence.__code__.co_consts
    assert b"maximumWidth" in names
    assert b"maximumHeight" in evidence_names
