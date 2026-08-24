from __future__ import annotations

import json
import uuid
from dataclasses import replace

import pytest

from athena.retrieval.protected_execution import ProtectedRuntimeExecutionGuard
from athena.retrieval.protected_source import (
    ProtectedRuntimeContextBundle,
    ProtectedRuntimeContextItem,
)


class _Verifier:
    def __init__(self) -> None:
        self.calls = 0
        self.failure: Exception | None = None

    def verify_bundle(self, bundle: ProtectedRuntimeContextBundle) -> None:
        self.calls += 1
        if self.failure is not None:
            raise self.failure


def _bundle() -> ProtectedRuntimeContextBundle:
    scope_id = uuid.uuid4()
    first_source = uuid.uuid4()
    second_source = uuid.uuid4()
    items = (
        ProtectedRuntimeContextItem(
            context_id="CTX-001",
            source_id=first_source,
            protection_scope_id=scope_id,
            source_name="secret-one.txt",
            source_uri="file:///secret-one.txt",
            mime_type="text/plain",
            document_hash=b"d" * 32,
            start_offset=0,
            end_offset=18,
            quoted_hash=b"q" * 32,
            text="protected secret 1",
            score=2.0,
            truncated=False,
        ),
        ProtectedRuntimeContextItem(
            context_id="CTX-002",
            source_id=second_source,
            protection_scope_id=scope_id,
            source_name="secret-two.txt",
            source_uri="file:///secret-two.txt",
            mime_type="text/plain",
            document_hash=b"e" * 32,
            start_offset=10,
            end_offset=28,
            quoted_hash=b"r" * 32,
            text="protected secret 2",
            score=1.0,
            truncated=False,
        ),
    )
    return ProtectedRuntimeContextBundle(
        query="secret",
        mode="protected_runtime_lexical",
        items=items,
        omitted_count=3,
        estimated_tokens=42,
        max_estimated_tokens=128,
        rendered_text="protected rendered secret",
    )


def test_guard_verifies_on_construction_and_immediately_before_provider_call() -> None:
    verifier = _Verifier()
    guard = ProtectedRuntimeExecutionGuard(verifier=verifier, bundle=_bundle())

    assert verifier.calls == 1

    guard.before_provider_call()

    assert verifier.calls == 2


def test_guard_propagates_reverification_failure_before_provider_call() -> None:
    verifier = _Verifier()
    guard = ProtectedRuntimeExecutionGuard(verifier=verifier, bundle=_bundle())
    verifier.failure = RuntimeError("scope relocked")

    with pytest.raises(RuntimeError, match="scope relocked"):
        guard.before_provider_call()

    assert verifier.calls == 2


def test_guard_durable_metadata_excludes_plaintext_and_plaintext_hashes() -> None:
    guard = ProtectedRuntimeExecutionGuard(verifier=_Verifier(), bundle=_bundle())

    metadata = dict(guard.durable_metadata())
    serialized = json.dumps(metadata, sort_keys=True)

    assert metadata["protected_runtime_context"] is True
    assert metadata["item_count"] == 2
    assert metadata["omitted_count"] == 3
    assert metadata["context_ids"] == ("CTX-001", "CTX-002")
    forbidden_keys = {
        "text",
        "rendered_text",
        "document_hash",
        "quoted_hash",
        "source_name",
        "source_uri",
        "query",
    }
    assert forbidden_keys.isdisjoint(metadata)
    assert "protected secret" not in serialized
    assert "protected rendered secret" not in serialized
    assert "secret-one" not in serialized
    assert "secret-two" not in serialized


def test_guard_rejects_untyped_bundle() -> None:
    with pytest.raises(TypeError, match="ProtectedRuntimeContextBundle"):
        ProtectedRuntimeExecutionGuard(
            verifier=_Verifier(),
            bundle=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("omitted_count", True),
        ("omitted_count", -1),
        ("estimated_tokens", False),
        ("estimated_tokens", -1),
        ("max_estimated_tokens", True),
        ("max_estimated_tokens", 0),
    ],
)
def test_guard_rejects_invalid_bundle_counters(field: str, value: object) -> None:
    bundle = replace(_bundle(), **{field: value})

    with pytest.raises((TypeError, ValueError)):
        ProtectedRuntimeExecutionGuard(verifier=_Verifier(), bundle=bundle)


def test_guard_rejects_bundle_that_exceeds_its_token_budget() -> None:
    bundle = replace(
        _bundle(),
        estimated_tokens=129,
        max_estimated_tokens=128,
    )

    with pytest.raises(ValueError, match="must not exceed"):
        ProtectedRuntimeExecutionGuard(verifier=_Verifier(), bundle=bundle)


def test_guard_rejects_unsupported_mode() -> None:
    bundle = replace(_bundle(), mode="hybrid")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="mode is unsupported"):
        ProtectedRuntimeExecutionGuard(verifier=_Verifier(), bundle=bundle)


def test_guard_rejects_blank_query_and_rendered_context() -> None:
    with pytest.raises(ValueError, match="query must be non-empty"):
        ProtectedRuntimeExecutionGuard(
            verifier=_Verifier(),
            bundle=replace(_bundle(), query=" "),
        )
    with pytest.raises(ValueError, match="rendered context must be non-empty"):
        ProtectedRuntimeExecutionGuard(
            verifier=_Verifier(),
            bundle=replace(_bundle(), rendered_text=""),
        )
