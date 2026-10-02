from __future__ import annotations

from PySide6.QtCore import QProcess, QProcessEnvironment

from athena.desktop.scheduler_supervisor import DesktopJobSchedulerSupervisor


class _Process:
    def __init__(
        self,
        *,
        waits: tuple[bool, ...] = (),
        write_result: int = len(b"stop\n"),
        start_ok: bool = True,
    ) -> None:
        self.program = ""
        self.arguments: list[str] = []
        self.environment: QProcessEnvironment | None = None
        self.channel_mode: QProcess.ProcessChannelMode | None = None
        self.process_state = QProcess.ProcessState.NotRunning
        self.waits = list(waits)
        self.write_result = write_result
        self.start_ok = start_ok
        self.writes: list[bytes] = []
        self.bytes_written_timeouts: list[int] = []
        self.wait_timeouts: list[int] = []
        self.start_wait_timeouts: list[int] = []
        self.terminate_calls = 0
        self.kill_calls = 0

    def state(self) -> QProcess.ProcessState:
        return self.process_state

    def setProgram(self, program: str) -> None:  # noqa: N802
        self.program = program

    def setArguments(self, arguments: list[str]) -> None:  # noqa: N802
        self.arguments = arguments

    def setProcessEnvironment(self, environment: QProcessEnvironment) -> None:  # noqa: N802
        self.environment = environment

    def setProcessChannelMode(self, mode: QProcess.ProcessChannelMode) -> None:  # noqa: N802
        self.channel_mode = mode

    def start(self) -> None:
        self.process_state = QProcess.ProcessState.Starting

    def waitForStarted(self, msecs: int = 30_000) -> bool:  # noqa: N802
        self.start_wait_timeouts.append(msecs)
        if not self.start_ok:
            self.process_state = QProcess.ProcessState.NotRunning
            return False
        self.process_state = QProcess.ProcessState.Running
        return True

    def errorString(self) -> str:  # noqa: N802
        return "start failed"

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return self.write_result

    def waitForBytesWritten(self, msecs: int = 30_000) -> bool:  # noqa: N802
        self.bytes_written_timeouts.append(msecs)
        return True

    def waitForFinished(self, msecs: int = 30_000) -> bool:  # noqa: N802
        self.wait_timeouts.append(msecs)
        result = self.waits.pop(0) if self.waits else False
        if result:
            self.process_state = QProcess.ProcessState.NotRunning
        return result

    def terminate(self) -> None:
        self.terminate_calls += 1

    def kill(self) -> None:
        self.kill_calls += 1


def _running_supervisor(process: _Process) -> DesktopJobSchedulerSupervisor:
    supervisor = DesktopJobSchedulerSupervisor(
        process=process,
        executable="python",
    )
    supervisor.start()
    return supervisor


def test_scheduler_launch_enables_owned_stdin_control() -> None:
    process = _Process()
    supervisor = _running_supervisor(process)

    assert process.arguments == [
        "-m",
        "athena",
        "job",
        "scheduler-run",
        "--worker",
        "pathena-desktop",
        "--lane",
        "supervisor",
        "--control-stdin",
    ]
    assert supervisor.child_active is True


def test_scheduler_stop_requests_graceful_control_before_terminate() -> None:
    process = _Process(waits=(True,))
    supervisor = _running_supervisor(process)

    supervisor.stop()

    assert process.writes == [b"stop\n"]
    assert process.bytes_written_timeouts == [500]
    assert process.wait_timeouts == [7_500]
    assert process.terminate_calls == 0
    assert process.kill_calls == 0
    assert supervisor.child_active is False
    assert supervisor.stopping is True


def test_scheduler_stop_falls_back_when_control_pipe_rejects_write() -> None:
    process = _Process(waits=(True,), write_result=-1)
    supervisor = _running_supervisor(process)

    supervisor.stop()

    assert process.writes == [b"stop\n"]
    assert process.bytes_written_timeouts == []
    assert process.wait_timeouts == [1_500]
    assert process.terminate_calls == 1
    assert process.kill_calls == 0


def test_scheduler_stop_escalates_after_grace_and_terminate_timeouts() -> None:
    process = _Process(waits=(False, False, True))
    supervisor = _running_supervisor(process)

    supervisor.stop()

    assert process.writes == [b"stop\n"]
    assert process.wait_timeouts == [7_500, 1_500, 1_000]
    assert process.terminate_calls == 1
    assert process.kill_calls == 1
    assert supervisor.child_active is False
