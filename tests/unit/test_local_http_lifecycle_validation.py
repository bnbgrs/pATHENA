from __future__ import annotations

import pytest

from athena.model.adapters.local_http import _BoundedLocalResponse


class _NonCallableEnterResponse:
    __enter__ = object()


class _NonCallableExitResponse:
    __exit__ = object()


class _NonCallableCloseResponse:
    close = object()


class _CallableLifecycleResponse:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __enter__(self) -> _CallableLifecycleResponse:
        self.entered = True
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.exited = True


def test_bounded_local_response_rejects_noncallable_enter_hook() -> None:
    bounded = _BoundedLocalResponse(_NonCallableEnterResponse(), max_bytes=4)

    with pytest.raises(OSError, match="__enter__ hook must be callable"):
        bounded.__enter__()

    assert bounded._bytes_read == 0


def test_bounded_local_response_rejects_noncallable_exit_hook() -> None:
    bounded = _BoundedLocalResponse(_NonCallableExitResponse(), max_bytes=4)

    with pytest.raises(OSError, match="__exit__ hook must be callable"):
        bounded.__exit__(None, None, None)

    assert bounded._bytes_read == 0


def test_bounded_local_response_rejects_noncallable_close_hook() -> None:
    bounded = _BoundedLocalResponse(_NonCallableCloseResponse(), max_bytes=4)

    with pytest.raises(OSError, match="close hook must be callable"):
        bounded.__exit__(None, None, None)

    assert bounded._bytes_read == 0


def test_bounded_local_response_preserves_callable_lifecycle_hooks() -> None:
    response = _CallableLifecycleResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    assert bounded.__enter__() is bounded
    assert response.entered is True
    assert bounded.__exit__(None, None, None) is None
    assert response.exited is True
