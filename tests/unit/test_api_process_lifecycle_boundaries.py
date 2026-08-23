from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import athena.api.process as process_module
from athena.api.process import CoreApiProcess, CoreApiProcessError
from athena.config.settings import AthenaSettings


@pytest.mark.parametrize("port", [True, False, 1234.5, "1234", -1, 65536])
def test_process_rejects_invalid_port_before_application_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    port: Any,
) -> None:
    def forbidden_application(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("application construction must not occur")

    monkeypatch.setattr(process_module, "AthenaApplication", forbidden_application)
    settings = AthenaSettings(local_root=tmp_path)

    with pytest.raises(ValueError, match="integer between 0 and 65535"):
        CoreApiProcess(settings=settings, port=port)  # type: ignore[arg-type]


class _FailingStop:
    def stop(self) -> None:
        raise RuntimeError("stop failed")


class _FailingOwnership:
    def close(self) -> None:
        raise RuntimeError("close failed")


def test_startup_rollback_never_masks_original_failure() -> None:
    process = CoreApiProcess.__new__(CoreApiProcess)
    process.server = _FailingStop()  # type: ignore[assignment]
    process.executor = _FailingStop()  # type: ignore[assignment]
    process._ownership = _FailingOwnership()  # type: ignore[assignment]

    process._rollback_startup()

    assert process._ownership is None


def test_main_translates_shutdown_failure_to_exit_code_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = AthenaSettings(local_root=tmp_path)

    class _Runtime:
        discovery_path = tmp_path / "discovery.json"

    class _Server:
        port = 1234
        runtime = _Runtime()

    class _Process:
        server = _Server()

        def __init__(self, *, settings: AthenaSettings, port: int) -> None:
            del settings, port

        def start(self) -> None:
            return None

        def wait(self) -> int:
            return 0

        def stop(self) -> None:
            raise CoreApiProcessError("shutdown failed")

    monkeypatch.setattr(
        process_module.AthenaSettings,
        "from_environment",
        classmethod(lambda cls: settings),
    )
    monkeypatch.setattr(process_module, "CoreApiProcess", _Process)

    assert process_module.main([]) == 2
