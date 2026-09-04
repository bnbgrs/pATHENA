from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

import pytest

from athena.retrieval.source_anchor import SearchSourceAnchorRef, source_anchor_ref


@dataclass(frozen=True)
class _ArchiveResultShape:
    representation_id: uuid.UUID
    start_anchor_value: int
    end_anchor_value: int
    content_hash: bytes


def test_source_anchor_ref_preserves_verified_archive_anchor_inputs() -> None:
    representation_id = uuid.uuid4()
    digest = hashlib.sha256(b"Berlin evidence").digest()
    result = _ArchiveResultShape(
        representation_id=representation_id,
        start_anchor_value=7,
        end_anchor_value=22,
        content_hash=digest,
    )

    anchor = source_anchor_ref(result)

    assert anchor == SearchSourceAnchorRef(
        representation_id=representation_id,
        start_offset=7,
        end_offset=22,
        quoted_hash=digest,
    )
    assert anchor.stable_key == (representation_id, 7, 22, digest)


@pytest.mark.parametrize(
    ("start_offset", "end_offset", "quoted_hash", "error_type"),
    [
        (True, 2, b"x" * 32, TypeError),
        (0, False, b"x" * 32, TypeError),
        (-1, 2, b"x" * 32, ValueError),
        (2, 2, b"x" * 32, ValueError),
        (0, 2, "not-bytes", TypeError),
        (0, 2, b"short", ValueError),
    ],
)
def test_search_source_anchor_ref_rejects_invalid_materialization_inputs(
    start_offset: object,
    end_offset: object,
    quoted_hash: object,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        SearchSourceAnchorRef(
            representation_id=uuid.uuid4(),
            start_offset=start_offset,  # type: ignore[arg-type]
            end_offset=end_offset,  # type: ignore[arg-type]
            quoted_hash=quoted_hash,  # type: ignore[arg-type]
        )
