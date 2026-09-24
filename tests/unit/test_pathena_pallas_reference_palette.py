from __future__ import annotations

from athena.desktop.pathena_pallas_field import _CANVAS, _node_color
from athena.desktop.pathena_pallas_semantic import PallasNodeKind, PallasSemanticNode
from athena.desktop.pathena_v3_theme import (
    V3_ACCENT,
    V3_BG,
    V3_DANGER,
    V3_MINT,
    V3_WARNING,
)


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


def test_pallas_canvas_uses_active_v3_canvas() -> None:
    assert _CANVAS.name().casefold() == V3_BG.casefold()


def test_pallas_v3_semantics_keep_meaningful_state_colors() -> None:
    assert _hex(PallasNodeKind.FOCUS) == V3_ACCENT.casefold()
    assert _hex(PallasNodeKind.SOURCE) == V3_MINT.casefold()
    assert _hex(PallasNodeKind.CLAIM) == V3_ACCENT.casefold()
    assert _hex(PallasNodeKind.KNOWLEDGE) == "#e6e0c8"
    assert _hex(PallasNodeKind.MEMORY) == "#afc7a0"
    assert _hex(PallasNodeKind.HYPOTHESIS) == V3_WARNING.casefold()
    assert _hex(PallasNodeKind.CONFLICT) == V3_DANGER.casefold()
    assert _hex(PallasNodeKind.UNCERTAIN) == V3_WARNING.casefold()
