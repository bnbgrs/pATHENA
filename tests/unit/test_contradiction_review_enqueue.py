from __future__ import annotations

import sqlite3
import uuid
from types import SimpleNamespace

from athena.knowledge import contradiction_review_enqueue as enqueue_module
from athena.knowledge.contradiction_review_enqueue import (
    enqueue_canonical_contradiction_review,
)
from athena.knowledge.review_service import ReviewService


def _arguments() -> dict[str, object]:
    return {
        "processing_run_id": uuid.uuid4(),
        "model_signature_id": uuid.uuid4(),
        "left_entity_id": uuid.uuid4(),
        "left_revision_id": uuid.uuid4(),
        "right_entity_id": uuid.uuid4(),
        "right_revision_id": uuid.uuid4(),
        "confidence": 0.91,
        "reason": "model-proposed contradiction",
        "created_at_us": 123456,
    }


def test_deterministic_rejection_creates_no_review(monkeypatch) -> None:
    connection = sqlite3.connect(":memory:")
    arguments = _arguments()
    calls: list[str] = []

    monkeypatch.setattr(
        enqueue_module,
        "assess_canonical_contradiction_candidate",
        lambda connection, *, left_revision_id, right_revision_id: SimpleNamespace(
            permits_contradiction_candidate=False
        ),
    )

    def unexpected_enqueue(*args: object, **kwargs: object) -> uuid.UUID:
        calls.append("enqueue")
        return uuid.uuid4()

    monkeypatch.setattr(ReviewService, "enqueue_contradiction", unexpected_enqueue)

    result = enqueue_canonical_contradiction_review(connection, **arguments)  # type: ignore[arg-type]

    assert result is None
    assert calls == []


def test_permitted_pair_delegates_exact_revision_and_review_metadata(monkeypatch) -> None:
    connection = sqlite3.connect(":memory:")
    arguments = _arguments()
    review_id = uuid.uuid4()
    assessed: list[tuple[uuid.UUID, uuid.UUID]] = []
    delegated: dict[str, object] = {}

    def permit(
        connection: sqlite3.Connection,
        *,
        left_revision_id: uuid.UUID,
        right_revision_id: uuid.UUID,
    ) -> SimpleNamespace:
        assessed.append((left_revision_id, right_revision_id))
        return SimpleNamespace(permits_contradiction_candidate=True)

    def enqueue(
        connection: sqlite3.Connection,
        **kwargs: object,
    ) -> uuid.UUID:
        delegated.update(kwargs)
        return review_id

    monkeypatch.setattr(enqueue_module, "assess_canonical_contradiction_candidate", permit)
    monkeypatch.setattr(ReviewService, "enqueue_contradiction", enqueue)

    result = enqueue_canonical_contradiction_review(connection, **arguments)  # type: ignore[arg-type]

    assert result == review_id
    assert assessed == [
        (
            arguments["left_revision_id"],
            arguments["right_revision_id"],
        )
    ]
    assert delegated == arguments
