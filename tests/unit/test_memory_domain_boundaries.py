from __future__ import annotations

import math
import uuid

import pytest

from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemoryDraft,
)


def _draft(**overrides: object) -> PersonalMemoryDraft:
    values: dict[str, object] = {
        "memory_kind": MemoryKind.RESPONSE_STYLE,
        "content": "Use concise Markdown.",
        "scope_kind": MemoryScopeKind.GLOBAL,
        "scope_entity_id": None,
        "learning_mode": MemoryLearningMode.EXPLICIT_USER,
        "sensitivity": MemorySensitivity.NORMAL,
        "confidence": None,
        "last_confirmed_at_us": None,
    }
    values.update(overrides)
    return PersonalMemoryDraft(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("memory_kind", "response_style", "MemoryKind"),
        ("scope_kind", "global", "MemoryScopeKind"),
        ("learning_mode", "explicit_user", "MemoryLearningMode"),
        ("sensitivity", "normal", "MemorySensitivity"),
    ],
)
def test_personal_memory_draft_rejects_untyped_enum_values(
    field: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        _draft(**{field: value})


@pytest.mark.parametrize("content", [None, b"text", 1])
def test_personal_memory_draft_requires_text_content(content: object) -> None:
    with pytest.raises(TypeError, match="content must be text"):
        _draft(content=content)


def test_personal_memory_draft_requires_uuid_for_scoped_identity() -> None:
    with pytest.raises(TypeError, match="scope_entity_id"):
        _draft(
            scope_kind=MemoryScopeKind.PROJECT,
            scope_entity_id="not-a-uuid",
        )


@pytest.mark.parametrize("confidence", [True, False, "0.9"])
def test_personal_memory_draft_rejects_non_numeric_confidence(
    confidence: object,
) -> None:
    with pytest.raises(TypeError, match="confidence"):
        _draft(
            learning_mode=MemoryLearningMode.MODEL_INFERRED,
            confidence=confidence,
        )


@pytest.mark.parametrize("confidence", [math.nan, math.inf, -math.inf])
def test_personal_memory_draft_rejects_non_finite_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValueError, match="finite"):
        _draft(
            learning_mode=MemoryLearningMode.MODEL_INFERRED,
            confidence=confidence,
        )


@pytest.mark.parametrize("timestamp", [True, False, 1.5, "1"])
def test_personal_memory_draft_requires_integer_confirmation_timestamp(
    timestamp: object,
) -> None:
    with pytest.raises(TypeError, match="last_confirmed_at_us"):
        _draft(last_confirmed_at_us=timestamp)


def test_personal_memory_draft_still_normalizes_valid_text() -> None:
    draft = _draft(
        content="  Use concise Markdown.  ",
        last_confirmed_at_us=0,
    )

    assert draft.content == "Use concise Markdown."
    assert draft.last_confirmed_at_us == 0
