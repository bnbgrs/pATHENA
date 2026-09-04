"""Target-workstation hardware acceptance controls for the SYSTEM workspace."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QProcess, QStandardPaths
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state


@dataclass(frozen=True, slots=True)
class HardwareAcceptancePresentation:
    status: str
    detail: str
    state: str


def default_hardware_acceptance_report_path() -> Path:
    """Return a durable per-user report path without writing beside the executable."""
    root = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation
    ).strip()
    if root:
        return Path(root) / "hardware-acceptance.json"
    return Path.home() / ".pathena" / "hardware-acceptance.json"


def hardware_acceptance_launch_spec(
    executable: str,
    report_path: Path,
) -> tuple[str, tuple[str, ...]]:
    """Build the source/frozen-safe worker invocation used by the SYSTEM UI."""
    normalized_executable = executable.strip()
    if not normalized_executable:
        raise ValueError("Hardware acceptance executable must not be empty.")
    return (
        normalized_executable,
        (
            "-m",
            "athena.hardware_acceptance",
            "--output",
            str(report_path),
            "--json",
        ),
    )


def project_hardware_acceptance_payload(
    payload: Mapping[str, object],
) -> HardwareAcceptancePresentation:
    """Project the machine report into a compact, evidence-preserving UI state."""
    overall = payload.get("overall_ready")
    if not isinstance(overall, bool):
        raise ValueError("Hardware acceptance report is missing overall_ready.")

    detected_raw = payload.get("detected_gpus")
    detected = tuple(
        value.strip()
        for value in detected_raw
        if isinstance(value, str) and value.strip()
    ) if isinstance(detected_raw, list) else ()
    gpu_label = detected[0] if detected else "GPU unavailable"

    model_raw = payload.get("selected_model_id")
    model_label = (
        model_raw.strip()
        if isinstance(model_raw, str) and model_raw.strip()
        else "no loaded model"
    )

    if overall:
        return HardwareAcceptancePresentation(
            status="PASS",
            detail=f"{gpu_label} · {model_label} · live inference passed",
            state="success",
        )

    checks = payload.get("checks")
    failure_detail: str | None = None
    if isinstance(checks, list):
        for raw_check in checks:
            if not isinstance(raw_check, Mapping):
                continue
            if raw_check.get("status") != "FAIL":
                continue
            raw_detail = raw_check.get("detail")
            if isinstance(raw_detail, str) and raw_detail.strip():
                failure_detail = raw_detail.strip()
                break
    return HardwareAcceptancePresentation(
        status="FAIL",
        detail=failure_detail or "Target hardware acceptance did not pass.",
        state="error",
    )


class SystemHardwareAcceptancePanel(QFrame):
    """Run the strict local hardware probe without blocking the Qt event loop."""

    def __init__(
        self,
        *,
        report_path: Path | None = None,
        executable: str | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("systemHardwareAcceptance")
        self.setProperty("pathenaTargetHardwareAcceptance", True)
        self._report_path = report_path or default_hardware_acceptance_report_path()
        self._executable = executable or sys.executable
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_process_error)

        labels = QVBoxLayout()
        labels.setContentsMargins(0, 0, 0, 0)
        labels.setSpacing(4)
        heading = QLabel("TARGET HARDWARE")
        heading.setProperty("role", "section")
        self.status = QLabel("NOT RUN")
        self.status.setObjectName("settingsValue")
        set_pathena_ui_state(self.status, "empty")
        labels.addWidget(heading)
        labels.addWidget(self.status)

        self.detail = QLabel(
            "Run on the actual Windows workstation to verify the expected GPU, "
            "a loaded LM Studio LLM, and one real local inference."
        )
        self.detail.setObjectName("settingsHelp")
        self.detail.setWordWrap(True)
        self.detail.setProperty("pathenaHardwareAcceptanceReport", str(self._report_path))

        self.run_button = QPushButton("RUN CHECK")
        self.run_button.setObjectName("newChatButton")
        self.run_button.setToolTip(
            "Run the strict target-workstation GPU and LM Studio inference acceptance"
        )
        self.run_button.setEnabled(os.name == "nt")
        self.run_button.clicked.connect(self.run_check)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(16)
        layout.addLayout(labels)
        layout.addWidget(self.detail, 1)
        layout.addWidget(self.run_button)

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.aboutToQuit.connect(self.stop)

        self.load_existing_report()

    @property
    def report_path(self) -> Path:
        return self._report_path

    def load_existing_report(self) -> bool:
        if not self._report_path.is_file():
            return False
        try:
            payload = json.loads(self._report_path.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise ValueError("Hardware acceptance report must be a JSON object.")
            presentation = project_hardware_acceptance_payload(payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self._apply_presentation(
                HardwareAcceptancePresentation(
                    status="INVALID",
                    detail=f"Stored hardware report is unreadable: {exc}",
                    state="error",
                )
            )
            return False
        self._apply_presentation(presentation)
        return True

    def run_check(self) -> bool:
        if os.name != "nt":
            self._apply_presentation(
                HardwareAcceptancePresentation(
                    status="UNAVAILABLE",
                    detail="Target hardware acceptance is supported only on Windows.",
                    state="empty",
                )
            )
            return False
        if self._process.state() != QProcess.ProcessState.NotRunning:
            return False

        try:
            self._report_path.parent.mkdir(parents=True, exist_ok=True)
            self._report_path.unlink(missing_ok=True)
            program, arguments = hardware_acceptance_launch_spec(
                self._executable,
                self._report_path,
            )
        except (OSError, ValueError) as exc:
            self._apply_presentation(
                HardwareAcceptancePresentation(
                    status="FAIL",
                    detail=f"Could not prepare hardware acceptance: {exc}",
                    state="error",
                )
            )
            return False

        self.status.setText("RUNNING")
        self.detail.setText(
            "Checking Windows GPU, loaded LM Studio model and one live local inference…"
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
        loaded = self.load_existing_report()
        if not loaded and self.status.text() != "INVALID":
            output = bytes(self._process.readAllStandardOutput().data()).decode(
                "utf-8", errors="replace"
            ).strip()
            clipped = output[-240:] if output else "no diagnostic output"
            self._apply_presentation(
                HardwareAcceptancePresentation(
                    status="FAIL",
                    detail=f"Hardware acceptance exited {exit_code}: {clipped}",
                    state="error",
                )
            )
        self.run_button.setText("RUN AGAIN")
        self.run_button.setEnabled(os.name == "nt")

    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.Crashed:
            detail = "Hardware acceptance process crashed before completion."
        else:
            detail = f"Hardware acceptance process error: {self._process.errorString()}"
        self._apply_presentation(
            HardwareAcceptancePresentation(status="FAIL", detail=detail, state="error")
        )
        if self._process.state() == QProcess.ProcessState.NotRunning:
            self.run_button.setEnabled(os.name == "nt")

    def _apply_presentation(self, presentation: HardwareAcceptancePresentation) -> None:
        self.status.setText(presentation.status)
        self.detail.setText(presentation.detail)
        set_pathena_ui_state(self.status, presentation.state)
        set_pathena_ui_state(self.detail, presentation.state)
        self.setProperty("pathenaHardwareAcceptanceStatus", presentation.status)
