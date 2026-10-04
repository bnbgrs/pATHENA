from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from athena.desktop.knowledge_cli import _safe


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Alpha\tBeta", "Alpha Beta"),
        ("Alpha\r\nBeta", "Alpha Beta"),
        ("Alpha\vBeta", "Alpha Beta"),
        ("Alpha\fBeta", "Alpha Beta"),
        ("Alpha\x85Beta", "Alpha Beta"),
        ("Alpha\u2028Beta", "Alpha Beta"),
        ("Alpha\u2029Beta", "Alpha Beta"),
    ],
)
def test_safe_fields_cannot_break_line_or_tsv_framing(
    raw: str,
    expected: str,
) -> None:
    assert _safe(raw) == expected


def test_safe_field_falls_back_after_only_framing_whitespace() -> None:
    assert _safe("\r\n\t") == "-"
