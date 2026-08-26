"""Read-only Recovery diagnostics for the pATHENA SYSTEM workspace."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state


@dataclass(frozen=True, slots=True)
class RecoveryPresentation:
    status: str
    detail: str
    state: str


def recovery_diagnose_launch_spec(executable: str) -> tuple[str, tuple[str, ...]]:
    """Build the source/frozen-safe read-only Recovery diagnosis invocation."""
    normalized_executable = executable.strip()
    if not normalized_executable:
        raise ValueError("Recovery diagnostic executable must not be empty.")
    return normalized_executable, ("-m", "athena.recovery_cli", "diagnose")


def _first_issue_action(payload: Mapping[str, object]) -> str | None:
    issues = payload.get("issues")
    if not isinstance(issues, list):
        return None
    for raw_issue in issues:
        if not isinstance(raw_issue, Mapping):
            continue
        action = raw_issue.get("action")
        if isinstance(action, str) and action.strip():
            return action.strip()
    return None


def project_recovery_payload(payload: Mapping[str, object]) -> RecoveryPresentation:
    """Project the payload-free Recovery matrix into a compact operator state."""
    raw_status = payload.get("status")
    if not isinstance(raw_status, str):
        raise ValueError("Recovery diagnosis is missing status.")
    status = raw_status.strip()

    canonical_raw = payload.get("canonical_database")
    canonical = (
        canonical_raw.strip()
        if isinstance(canonical_raw, str) and canonical_raw.strip()
        else "unknown"
    )
    normal_start = payload.get("normal_core_start_allowed")
    if not isinstance(normal_start, bool):
        raise ValueError("Recovery diagnosis is missing normal_core_start_allowed.")

    action = _first_issue_action(payload)
    if status == "healthy":
        return RecoveryPresentation(
            status="HEALTHY",
            detail=f"Canonical database {canonical}; normal Core start allowed.",
            state="success",
        )
    if status == "degraded-derived":
        suffix = action or "rebuild Derived State"
        return RecoveryPresentation(
            status="REBUILD NEEDED",
            detail=f"Canonical database {canonical}; {suffix}.",
            state="busy",
        )
    if status == "recovery-required":
        suffix = action or "operator recovery review required"
        return RecoveryPresentation(
            status="RECOVERY REQUIRED",
            detail=f"Normal Core start blocked; {suffix}.",
            state="error",
        )
    raise ValueError(f"Unsupported Recovery diagnostic status: {status!r}.")


class SystemRecoveryPanel(QFrame):
    """Run payload-free Recovery diagnostics without blocking the Qt event loop."""

    def __init__(self, *, executable: str | None = None) -> None:
        super().__init__()
        self.setObjectName("systemRecoveryPanel")
        self.setProperty("pathenaRecoveryReadOnly", True)
        self.setProperty("pathenaRecoveryRestoreAvailable", False)
        self._executable = executable or sys.executable
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_process_error)

        labels = QVBoxLayout()
        labels.setContentsMargins(0, 0, 0, 0)
        labels.setSpacing(4)
        heading = QLabel("RECOVERY")
        heading.setProperty("role", "section")
        self.status = QLabel("NOT CHECKED")
        self.status.setObjectName("settingsValue")
        set_pathena_ui_state(self.status, "empty")
        labels.addWidget(heading)
        labels.addWidget(self.status)

        self.detail = QLabel(
            "Read-only diagnosis of the canonical database and rebuildable Derived State. "
            "This control never restores or repairs data automatically."
        )
        self.detail.setObjectName("settingsHelp")
        self.detail.setWordWrap(True)

        self.run_button = QPushButton("RUN DIAGNOSIS")
        self.run_button.setObjectName("newChatButton")
        self.run_button.setToolTip(
            "Run payload-free read-only Recovery diagnostics without starting a repair"
        )
        self.run_button.clicked.connect(self.run_diagnosis)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(16)
        layout.addLayout(labels)
        layout.addWidget(self.detail, 1)
        layout.addWidget(self.run_button)

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.aboutToQuit.connect(self.stop)

    def run_diagnosis(self) -> bool:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            return False
        try:
            program, arguments = recovery_diagnose_launch_spec(self._executable)
        except ValueError as exc:
            self._apply_presentation(
                RecoveryPresentation("FAIL", str(exc), "error")
            )
            return False

        self.status.setText("RUNNING")
        self.detail.setText(
            "Inspecting canonical integrity and Derived State read-only; no repair is running…"
        )
        set_pathena_ui_state(self.status, "busy")
        set_pathena_ui_state(self.detail, "busy")
        self.run_button.setEnabled(False)
        self._process.setProgram(program)
        self._process.setArguments(list(arguments))
        self._process.start()
        return True

    def stop(self) -> None:
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return
        self._process.terminate()
        if not self._process.waitForFinished(1_500):
            self._process.kill()
            self._process.waitForFinished(1_000)

    def _handle_finished(self, exit_code: int, _exit_status: object) -> None:
        output = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        ).strip()
        try:
            lines = tuple(line.strip() for line in output.splitlines() if line.strip())
            if not lines:
                raise ValueError("Recovery diagnosis returned no output.")
            payload = json.loads(lines[-1])
            if not isinstance(payload, Mapping):
                raise ValueError("Recovery diagnosis must return a JSON object.")
            presentation = project_recovery_payload(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            clipped = output[-220:] if output else "no diagnostic output"
            presentation = RecoveryPresentation(
                status="FAIL",
                detail=f"Recovery diagnosis exited {exit_code}: {exc}; {clipped}",
                state="error",
            )
        self._apply_presentation(presentation)
        self.run_button.setText("RUN AGAIN")
        self.run_button.setEnabled(True)

    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.Crashed:
            detail = "Recovery diagnostic process crashed before completion."
        else:
            detail = f"Recovery diagnostic process error: {self._process.errorString()}"
        self._apply_presentation(RecoveryPresentation("FAIL", detail, "error"))
        self.run_button.setEnabled(True)

    def _apply_presentation(self, presentation: RecoveryPresentation) -> None:
        self.status.setText(presentation.status)
        self.detail.setText(presentation.detail)
        set_pathena_ui_state(self.status, presentation.state)
        set_pathena_ui_state(self.detail, presentation.state)
