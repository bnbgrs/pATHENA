"""Provider wrapper that journals raw Grounded stream deltas before persistence."""

from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from typing import Any

from athena.chat.grounded_partial_output import GroundedPartialOutputRepository
from athena.model.domain import ModelChatMessage
from athena.model.ports import ChatModelProvider


class GroundedCheckpointingProvider:
    """Delegate provider calls while durably recording each emitted chat delta."""

    def __init__(
        self,
        base: ChatModelProvider,
        *,
        partial_output: GroundedPartialOutputRepository,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        initial_attempt_no: int = 0,
    ) -> None:
        self._base = base
        self._partial_output = partial_output
        self._operation_id = operation_id
        if (
            isinstance(initial_attempt_no, bool)
            or not isinstance(initial_attempt_no, int)
            or initial_attempt_no < 0
        ):
            raise ValueError(
                "Grounded checkpoint initial_attempt_no must be non-negative."
            )
        self._chat_id = chat_id
        self._next_attempt_no = initial_attempt_no

    def __getattr__(self, name: str) -> Any:
        if name == "stream_chat_cancellable":
            method = getattr(self._base, name)

            def cancellable(**kwargs: Any) -> Iterator[str]:
                attempt_no = self._claim_attempt_no()
                for chunk in method(**kwargs):
                    self._record(attempt_no, chunk)
                    yield chunk

            return cancellable
        return getattr(self._base, name)

    @property
    def provider_id(self) -> str:
        return self._base.provider_id

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        attempt_no = self._claim_attempt_no()
        if temperature is not None:
            stream = self._base.stream_chat(
                model_id=model_id,
                messages=messages,
                max_output_tokens=max_output_tokens,
                reasoning_mode=reasoning_mode,
                temperature=temperature,
            )
        elif reasoning_mode is not None:
            stream = self._base.stream_chat(
                model_id=model_id,
                messages=messages,
                max_output_tokens=max_output_tokens,
                reasoning_mode=reasoning_mode,
            )
        elif max_output_tokens is not None:
            stream = self._base.stream_chat(
                model_id=model_id,
                messages=messages,
                max_output_tokens=max_output_tokens,
            )
        else:
            stream = self._base.stream_chat(
                model_id=model_id,
                messages=messages,
            )
        for chunk in stream:
            self._record(attempt_no, chunk)
            yield chunk

    def _claim_attempt_no(self) -> int:
        attempt_no = self._next_attempt_no
        self._next_attempt_no += 1
        return attempt_no

    def _record(self, attempt_no: int, chunk: str) -> None:
        self._partial_output.append(
            operation_id=self._operation_id,
            chat_id=self._chat_id,
            attempt_no=attempt_no,
            content=chunk,
        )
