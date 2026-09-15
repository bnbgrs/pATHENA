from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_pallas_field import _CANVAS, _node_color
from athena.desktop.pathena_pallas_semantic import PallasNodeKind, PallasSemanticNode


def _node(kind: PallasNodeKind) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=f"node:{kind.value}",
        kind=kind,
        entity_type=kind.value,
        entity_id=kind.value,
        revision_id=None,
        title=kind.value.title(),
        summary="Reference palette regression node.",
        epistemic_status=None,
        cited=True,
    )


def _hex(kind: PallasNodeKind) -> str:
    return _node_color(_node(kind)).name().casefold()


def test_pallas_canvas_uses_canonical_reference_canvas() -> None:
    assert _CANVAS.name().casefold() == PALETTE.canvas.casefold()


def test_pallas_reference_semantics_keep_distinct_reference_colors() -> None:
    assert _hex(PallasNodeKind.FOCUS) == PALETTE.accent.casefold()
    assert _hex(PallasNodeKind.SOURCE) == PALETTE.accent.casefold()
    assert _hex(PallasNodeKind.CLAIM) == PALETTE.success.casefold()
    assert _hex(PallasNodeKind.KNOWLEDGE) == PALETTE.success.casefold()
    assert _hex(PallasNodeKind.MEMORY) == PALETTE.success.casefold()
    assert _hex(PallasNodeKind.HYPOTHESIS) == PALETTE.question.casefold()
    assert _hex(PallasNodeKind.CONFLICT) == PALETTE.error.casefold()
    assert _hex(PallasNodeKind.UNCERTAIN) == PALETTE.warning.casefold()


def test_pallas_reference_semantics_do_not_reintroduce_legacy_orange() -> None:
    legacy_orange = "#f26a21"
    assert all(
        _hex(kind) != legacy_orange
        for kind in (
            PallasNodeKind.FOCUS,
            PallasNodeKind.SOURCE,
            PallasNodeKind.CLAIM,
            PallasNodeKind.KNOWLEDGE,
            PallasNodeKind.HYPOTHESIS,
            PallasNodeKind.MEMORY,
            PallasNodeKind.CONFLICT,
            PallasNodeKind.UNCERTAIN,
        )
    )
