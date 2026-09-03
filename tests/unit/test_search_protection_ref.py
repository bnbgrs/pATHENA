from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest

from athena.retrieval.protection import (
    SearchProtectionRef,
    SearchProtectionState,
    protected_search_protection_ref,
    unprotected_search_protection_ref,
)


@dataclass(frozen=True)
class _ProtectedResultShape:
    protection_scope_id: uuid.UUID


def test_unprotected_search_protection_ref_has_no_scope() -> None:
    protection = unprotected_search_protection_ref()

    assert protection == SearchProtectionRef(
        state=SearchProtectionState.UNPROTECTED,
        protection_scope_id=None,
    )


def test_protected_search_protection_ref_preserves_scope_id() -> None:
    scope_id = uuid.uuid4()

    protection = protected_search_protection_ref(
        _ProtectedResultShape(protection_scope_id=scope_id)
    )

    assert protection == SearchProtectionRef(
        state=SearchProtectionState.PROTECTED,
        protection_scope_id=scope_id,
    )


def test_unprotected_search_protection_ref_rejects_scope_metadata() -> None:
    with pytest.raises(ValueError):
        SearchProtectionRef(
            state=SearchProtectionState.UNPROTECTED,
            protection_scope_id=uuid.uuid4(),
        )


@pytest.mark.parametrize("scope_id", [None, True, "scope", object()])
def test_protected_search_protection_ref_rejects_invalid_scope_id(
    scope_id: object,
) -> None:
    with pytest.raises(TypeError):
        SearchProtectionRef(
            state=SearchProtectionState.PROTECTED,
            protection_scope_id=scope_id,  # type: ignore[arg-type]
        )


def test_protected_result_adapter_rejects_invalid_scope_id() -> None:
    @dataclass(frozen=True)
    class _MalformedProtectedResult:
        protection_scope_id: object

    with pytest.raises(TypeError):
        protected_search_protection_ref(
            _MalformedProtectedResult(protection_scope_id=True)  # type: ignore[arg-type]
        )
