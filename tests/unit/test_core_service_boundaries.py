from __future__ import annotations

import pytest

from athena.core.errors import ShutdownError, StartupError
from athena.core.services import ServiceManager


class _Service:
    def __init__(
        self,
        name: str,
        *,
        fail_start: bool = False,
        fail_stop: bool = False,
    ) -> None:
        self.name = name
        self.fail_start = fail_start
        self.fail_stop = fail_stop
        self.started = False
        self.stopped = False

    def start(self) -> None:
        if self.fail_start:
            raise RuntimeError("start failure")
        self.started = True

    def stop(self) -> None:
        self.stopped = True
        if self.fail_stop:
            raise RuntimeError("stop failure")


def test_service_manager_rejects_non_tuple() -> None:
    with pytest.raises(TypeError, match="tuple"):
        ServiceManager([])  # type: ignore[arg-type]


def test_service_manager_rejects_duplicate_names() -> None:
    with pytest.raises(ValueError, match="unique"):
        ServiceManager((_Service("same"), _Service("same")))


def test_service_manager_rejects_noncanonical_name() -> None:
    with pytest.raises(ValueError, match="canonical"):
        ServiceManager((_Service(" bad "),))


def test_service_manager_rolls_back_started_services() -> None:
    first = _Service("first")
    second = _Service("second", fail_start=True)
    manager = ServiceManager((first, second))

    with pytest.raises(StartupError, match="second"):
        manager.start_all()

    assert first.started is True
    assert first.stopped is True
    assert manager.started_service_names == ()


def test_service_manager_preserves_cached_name_during_stop_failure() -> None:
    service = _Service("stable", fail_stop=True)
    manager = ServiceManager((service,))
    manager.start_all()
    service.name = "mutated"

    with pytest.raises(ShutdownError, match="stable"):
        manager.stop_all()
