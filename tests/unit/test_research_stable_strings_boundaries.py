from __future__ import annotations

import uuid

import pytest

from athena.research.service import (
    ResearchConfigurationError,
    _stable_source_types,
    _stable_strings,
    _stable_uuids,
)
from athena.source.models import SourceType


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


@pytest.mark.parametrize(
    "value",
    ["not-a-sequence", b"uuid", bytearray(b"uuid"), {uuid.uuid4()}],
)
def test_stable_uuids_rejects_non_sequence_containers(value: object) -> None:
    with pytest.raises(ResearchConfigurationError, match="sequence of UUID values"):
        _stable_uuids(value)


def test_stable_uuids_preserves_deterministic_uuid_normalization() -> None:
    first = uuid.UUID("00000000-0000-0000-0000-000000000001")
    second = uuid.UUID("00000000-0000-0000-0000-000000000002")
    assert _stable_uuids([second, first, second]) == (first, second)


@pytest.mark.parametrize(
    "value",
    [set(SourceType), {next(iter(SourceType))}],
)
def test_stable_source_types_rejects_non_sequence_containers(value: object) -> None:
    with pytest.raises(
        ResearchConfigurationError, match="sequence of SourceType values"
    ):
        _stable_source_types(value)


def test_stable_source_types_preserves_deterministic_normalization() -> None:
    values = list(SourceType)
    assert values
    expected = tuple(sorted({item.value for item in values}))
    assert _stable_source_types([*reversed(values), values[0]]) == expected
