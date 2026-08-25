from __future__ import annotations

import pytest

from athena.desktop.packaged_app import (
    PackagedInvocationError,
    PackagedTarget,
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
