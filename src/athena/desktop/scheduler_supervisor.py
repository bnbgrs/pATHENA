"""Lifecycle supervision for pATHENA's durable scheduler supervisor process."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Slot

from athena.desktop.supervisor import core_process_launch_spec

_START_TIMEOUT_MS = 5_000
_TERMINATE_TIMEOUT_MS = 2_500
_KILL_TIMEOUT_MS = 1_000
_VENV_LAUNCHER_ENV = "__PYVENV_LAUNCHER__"
_SCHEDULER_ARGUMENTS = (
    "-m",
    "athena",
    "job",
    "scheduler-run",
    "--worker",
    "pathena-desktop",
    "--lane",
    "supervisor",
)


@dataclass(frozen=True, slots=True)
class SchedulerProcessLaunchSpec:
    """Resolved scheduler launch preserving the desktop Python environment."""

    program: str
    arguments: tuple[str, ...]
    venv_launcher: str | None = None


class ManagedSchedulerProcess(Protocol):
    def state(self) -> QProcess.ProcessState: ...

    def setProgram(self, program: str) -> None: ...  # noqa: N802

    def setArguments(self, arguments: list[str]) -> None: ...  # noqa: N802

    def setProcessEnvironment(self, environment: QProcessEnvironment) -> None: ...  # noqa: N802

    def setProcessChannelMode(
        self, mode: QProcess.ProcessChannelMode
    ) -> None: ...  # noqa: N802

    def start(self) -> None: ...

    def waitForStarted(self, msecs: int = ...) -> bool: ...  # noqa: N802

    def errorString(self) -> str: ...  # noqa: N802

    def waitForFinished(self, msecs: int = ...) -> bool: ...  # noqa: N802

    def terminate(self) -> None: ...

    def kill(self) -> None: ...


def scheduler_process_launch_spec(
    *,
    executable: str | None = None,
) -> SchedulerProcessLaunchSpec:
    """Resolve the canonical scheduler supervisor command for this runtime."""
    if executable is None:
        base = core_process_launch_spec()
    else:
        base = core_process_launch_spec(
            executable=executable,
            base_executable=executable,
        )
    return SchedulerProcessLaunchSpec(
        program=base.program,
        arguments=_SCHEDULER_ARGUMENTS,
        venv_launcher=base.venv_launcher,
    )


class DesktopJobSchedulerSupervisor(QObject):
    """Own the scheduler supervisor and restart it after unexpected exits."""

    def __init__(
        self,
        *,
        process: ManagedSchedulerProcess | None = None,
        executable: str | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.process = cast(ManagedSchedulerProcess, process or QProcess(self))
        self.launch_spec = scheduler_process_launch_spec(executable=executable)
        self._stopping = False

    @property
    def child_active(self) -> bool:
        return self.process.state() is not QProcess.ProcessState.NotRunning

    @property
    def stopping(self) -> bool:
        return self._stopping

    @Slot()
    def start(self) -> None:
        if self.child_active:
            return

        self._stopping = False
        environment = QProcessEnvironment.systemEnvironment()
        environment.remove(_VENV_LAUNCHER_ENV)
        if self.launch_spec.venv_launcher is not None:
            environment.insert(_VENV_LAUNCHER_ENV, self.launch_spec.venv_launcher)

        self.process.setProgram(self.launch_spec.program)
        self.process.setArguments(list(self.launch_spec.arguments))
        self.process.setProcessEnvironment(environment)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
        self.process.start()

        if not self.process.waitForStarted(_START_TIMEOUT_MS):
            detail = self.process.errorString().strip() or "unknown QProcess startup error"
            raise RuntimeError(
                f"pATHENA durable scheduler process failed to start: {detail}"
            )

    @Slot()
    def ensure_running(self) -> None:
        if self._stopping or self.child_active:
            return
        try:
            self.start()
        except RuntimeError:
            # Keep the desktop alive; the heartbeat retries transient launch failures.
            return

    @Slot()
    def stop(self) -> None:
        self._stopping = True
        if not self.child_active:
            return

        self.process.terminate()
        if self.process.waitForFinished(_TERMINATE_TIMEOUT_MS):
            return

        self.process.kill()
        self.process.waitForFinished(_KILL_TIMEOUT_MS)


def scheduler_process_command(
    *,
    executable: str | None = None,
) -> tuple[str, ...]:
    """Expose the exact uv-free scheduler command for packaging/tests."""
    spec = scheduler_process_launch_spec(executable=executable)
    return (spec.program, *spec.arguments)
