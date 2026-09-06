from __future__ import annotations

import pytest

from athena.model.adapters.local_http import (
    LocalResponseTooLargeError,
    _BoundedLocalResponse,
)


class _OversizedReadResponse:
    def read(self, size: int) -> bytes:
        return b"x" * (size + 1)


class _OversizedLineResponse:
    def readline(self, size: int) -> bytes:
        return b"x" * (size + 1)


def test_oversized_read_rejects_before_byte_accounting_mutates() -> None:
    bounded = _BoundedLocalResponse(_OversizedReadResponse(), max_bytes=4)

    with pytest.raises(LocalResponseTooLargeError):
        bounded.read()

    assert bounded._bytes_read == 0


def test_oversized_readline_rejects_before_byte_accounting_mutates() -> None:
    bounded = _BoundedLocalResponse(_OversizedLineResponse(), max_bytes=4)

    with pytest.raises(LocalResponseTooLargeError):
        bounded.readline()

    assert bounded._bytes_read == 0
