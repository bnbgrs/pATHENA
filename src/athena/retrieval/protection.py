"""Deterministic Search Response protection labels for retrieval results."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class SearchProtectionState(str, Enum):
    """Protection classification carried by a Search Response result."""

    UNPROTECTED = "unprotected"
    PROTECTED = "protected"


class _ProtectedSearchResult(Protocol):
    protection_scope_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class SearchProtectionRef:
    """Non-persisting protection label for a Search Response result.

    The label describes the protection class of a result, not whether a scope is
    currently unlocked. Protected results retain their scope id so downstream
    mixed-search/context code can preserve authorization boundaries. Unprotected
    results must never carry a protection scope id.
    """

    state: SearchProtectionState
    protection_scope_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, SearchProtectionState):
            raise TypeError("Search protection state must be a SearchProtectionState.")
        if self.state is SearchProtectionState.UNPROTECTED:
            if self.protection_scope_id is not None:
                raise ValueError(
                    "Unprotected Search results must not carry a protection_scope_id."
                )
            return
        if not isinstance(self.protection_scope_id, uuid.UUID):
            raise TypeError(
                "Protected Search results must carry a UUID protection_scope_id."
            )


def unprotected_search_protection_ref() -> SearchProtectionRef:
    """Return the protection label for the unprotected retrieval pipelines."""

    return SearchProtectionRef(state=SearchProtectionState.UNPROTECTED)


def protected_search_protection_ref(
    result: _ProtectedSearchResult,
) -> SearchProtectionRef:
    """Preserve the authorized ProtectionScope carried by a protected result."""

    scope_id = result.protection_scope_id
    if not isinstance(scope_id, uuid.UUID):
        raise TypeError(
            "Protected Search result protection_scope_id must be a UUID."
        )
    return SearchProtectionRef(
        state=SearchProtectionState.PROTECTED,
        protection_scope_id=scope_id,
    )
