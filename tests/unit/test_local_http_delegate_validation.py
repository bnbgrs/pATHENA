from __future__ import annotations

import pytest

from athena.model.adapters.local_http import _BoundedLocalResponse


class _MissingReadResponse:
    pass


class _NonCallableReadResponse:
    read = b"not-callable"


class _NonCallableReadlineResponse:
    readline = object()


@pytest.mark.parametrize("response", [_MissingReadResponse(), _NonCallableReadResponse()])
def test_bounded_local_response_rejects_invalid_read_delegate_before_accounting(
    response: object,
) -> None:
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    with pytest.raises(OSError, match="bounded read access"):
        bounded.read()

    assert bounded._bytes_read == 0


def test_bounded_local_response_rejects_invalid_readline_delegate_before_accounting() -> None:
    bounded = _BoundedLocalResponse(_NonCallableReadlineResponse(), max_bytes=4)

    with pytest.raises(OSError, match="bounded readline access"):
        bounded.readline()

    assert bounded._bytes_read == 0
