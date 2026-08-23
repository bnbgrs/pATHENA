from __future__ import annotations

from athena.desktop.ascii_panel import _COLS, _ROWS, _sample_indices, ascii_scene


def test_compact_pallas_sampling_preserves_semantic_center() -> None:
    compact_cols = _sample_indices(_COLS, 98.0, 5.0)
    compact_rows = _sample_indices(_ROWS, 157.0, 7.0)

    assert len(compact_cols) < _COLS
    assert len(compact_rows) < _ROWS
    assert _COLS // 2 in compact_cols
    assert _ROWS // 2 in compact_rows


def test_large_pallas_canvas_keeps_full_grid() -> None:
    assert _sample_indices(_COLS, 179.0, 5.0) == tuple(range(_COLS))
    assert _sample_indices(_ROWS, 301.0, 7.0) == tuple(range(_ROWS))


def test_sampling_does_not_change_underlying_semantic_scene() -> None:
    scene = ascii_scene("knowledge")

    assert len(scene) == _ROWS
    assert all(len(row) == _COLS for row in scene)
