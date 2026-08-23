from __future__ import annotations

from athena.desktop import pathena_interaction_refinement as refinement


def test_interaction_refinement_uses_short_lightweight_motion() -> None:
    assert refinement._ANIMATION_MS == 140
    assert refinement._COMPACT_WIDTH < refinement._COMFORTABLE_WIDTH


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
