from __future__ import annotations

from athena.desktop.pathena_pallas_field import _CANVAS, _node_color
from athena.desktop.pathena_pallas_semantic import PallasNodeKind, PallasSemanticNode
from athena.desktop.pathena_v2_theme import V2_ACCENT, V2_BG, V2_DANGER, V2_SUCCESS


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


def test_pallas_canvas_uses_v2_canvas() -> None:
    assert _CANVAS.name().casefold() == V2_BG.casefold()


def test_pallas_v2_semantics_keep_distinct_workspace_colors() -> None:
    assert _hex(PallasNodeKind.FOCUS) == V2_ACCENT.casefold()
    assert _hex(PallasNodeKind.SOURCE) == "#5fa8ff"
    assert _hex(PallasNodeKind.CLAIM) == V2_SUCCESS.casefold()
    assert _hex(PallasNodeKind.KNOWLEDGE) == "#a78bfa"
    assert _hex(PallasNodeKind.MEMORY) == "#a78bfa"
    assert _hex(PallasNodeKind.HYPOTHESIS) == "#f2c66d"
    assert _hex(PallasNodeKind.CONFLICT) == V2_DANGER.casefold()
    assert _hex(PallasNodeKind.UNCERTAIN) == "#f2c66d"
