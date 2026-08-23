from __future__ import annotations

import uuid

import pytest

from athena.knowledge.claim_service import ClaimService
from athena.knowledge.models import ClaimKind
from athena.knowledge.service import ChatMessageSequenceError


class _ChatStub:
    def __init__(self) -> None:
        self.load_calls = 0

    def load_chat(self, chat_id: uuid.UUID) -> object:
        self.load_calls += 1
        raise AssertionError(f"unexpected load for {chat_id}")


@pytest.mark.parametrize("sequence_no", [True, False, 0, -1, 1.0, 1.5, "1", None])
def test_claim_promotion_rejects_non_integer_sequence_before_chat_load(
    sequence_no: object,
) -> None:
    chat = _ChatStub()
    service = ClaimService(object(), chat)  # type: ignore[arg-type]

    with pytest.raises(ChatMessageSequenceError, match="integer of at least 1"):
        service.promote_chat_message(
            chat_id=uuid.uuid4(),
            sequence_no=sequence_no,  # type: ignore[arg-type]
            claim_kind=ClaimKind.FACT,
        )

    assert chat.load_calls == 0
