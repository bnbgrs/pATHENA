from __future__ import annotations

import pytest

from athena.research.service import ResearchConfigurationError, _stable_strings


@pytest.mark.parametrize("value", ["example.com", b"example.com", bytearray(b"example.com")])
def test_stable_strings_rejects_scalar_text_like_containers(value: object) -> None:
    with pytest.raises(ResearchConfigurationError, match="sequence of text values"):
        _stable_strings(value, field="domains")  # type: ignore[arg-type]


def test_stable_strings_preserves_valid_normalization() -> None:
    assert _stable_strings([" b.example ", "a.example", "a.example"], field="domains") == (
        "a.example",
        "b.example",
    )


def test_stable_strings_rejects_non_text_elements() -> None:
    with pytest.raises(ResearchConfigurationError, match="text values only"):
        _stable_strings(["a.example", 7], field="domains")  # type: ignore[list-item]
