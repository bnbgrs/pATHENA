from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from athena.desktop.packaged_app import (
    PackagedInvocationError,
    PackagedTarget,
    packaged_worker_path,
    prepare_frozen_desktop_runtime,
    route_packaged_argv,
)


def test_plain_frozen_start_routes_to_real_desktop() -> None:
    invocation = route_packaged_argv(())

    assert invocation.target is PackagedTarget.DESKTOP
    assert invocation.arguments == ()


def test_internal_core_module_routes_without_desktop_recursion() -> None:
    invocation = route_packaged_argv(("-m", "athena.api.process", "--port", "0"))

    assert invocation.target is PackagedTarget.CORE
    assert invocation.arguments == ("--port", "0")


def test_scheduler_and_lane_modules_route_through_athena_cli() -> None:
    invocation = route_packaged_argv(
        (
            "-m",
            "athena",
            "job",
            "scheduler-run",
            "--worker",
            "pathena-desktop-control",
            "--lane",
            "control",
        )
    )

    assert invocation.target is PackagedTarget.ATHENA_CLI
    assert invocation.arguments[:3] == ("job", "scheduler-run", "--worker")


def test_jobs_workspace_helper_routes_to_jobs_cli() -> None:
    invocation = route_packaged_argv(
        ("-m", "athena.desktop.jobs_cli", "list", "--limit", "150")
    )

    assert invocation.target is PackagedTarget.JOBS_CLI
    assert invocation.arguments == ("list", "--limit", "150")


def test_hardware_acceptance_routes_only_to_worker_role() -> None:
    invocation = route_packaged_argv(
        (
            "-m",
            "athena.hardware_acceptance",
            "--json",
            "--output",
            "hardware-acceptance.json",
        )
    )

    assert invocation.target is PackagedTarget.HARDWARE_ACCEPTANCE
    assert invocation.arguments == (
        "--json",
        "--output",
        "hardware-acceptance.json",
    )


def test_recovery_diagnostics_route_only_to_explicit_worker_role() -> None:
    invocation = route_packaged_argv(
        ("-m", "athena.recovery_cli", "diagnose")
    )

    assert invocation.target is PackagedTarget.RECOVERY
    assert invocation.arguments == ("diagnose",)


def test_frozen_desktop_binds_sys_executable_to_sibling_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    desktop = tmp_path / "pATHENA.exe"
    worker = tmp_path / "pATHENA-Worker.exe"
    desktop.write_bytes(b"desktop")
    worker.write_bytes(b"worker")
    monkeypatch.setattr(sys, "executable", str(desktop))
    monkeypatch.delenv("PATHENA_PACKAGED_DESKTOP_EXECUTABLE", raising=False)

    resolved = prepare_frozen_desktop_runtime(
        executable=str(desktop),
        frozen=True,
    )

    assert resolved == worker
    assert Path(sys.executable) == worker
    assert os.environ["PATHENA_PACKAGED_DESKTOP_EXECUTABLE"] == str(desktop.resolve())
    assert packaged_worker_path(str(desktop)) == worker


def test_incomplete_frozen_package_fails_before_desktop_start(
    tmp_path: Path,
) -> None:
    desktop = tmp_path / "pATHENA.exe"
    desktop.write_bytes(b"desktop")

    with pytest.raises(PackagedInvocationError, match="missing pATHENA-Worker.exe"):
        prepare_frozen_desktop_runtime(
            executable=str(desktop),
            frozen=True,
        )


@pytest.mark.parametrize(
    "argv",
    (
        ("-m",),
        ("-m", ""),
        ("-m", "athena.desktop.app"),
        ("-m", "unknown.module"),
    ),
)
def test_unknown_or_incomplete_module_dispatch_fails_closed(
    argv: tuple[str, ...],
) -> None:
    with pytest.raises(PackagedInvocationError):
        route_packaged_argv(argv)
