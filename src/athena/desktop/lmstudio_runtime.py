"""Headless LM Studio runtime control for the pATHENA desktop.

The controller keeps the GUI honest: it only reports commands that actually ran,
uses LM Studio's CLI for daemon/server lifecycle and model loading, and lets the
Core remain the source of truth for discovered/loaded model state.
"""

from __future__ import annotations

import os
import shutil
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urlparse

from PySide6.QtCore import QObject, QProcess, QSettings, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.pathena_window import PathenaMainWindow

_SETTINGS_ROOT: Final = "desktop/lmstudio-runtime/v1"
_DEFAULT_BASE_URL: Final = "http://127.0.0.1:1234"
_MODEL_VERIFY_INTERVAL_MS: Final = 750
_MODEL_VERIFY_REFRESH_LIMIT: Final = 5
_MODEL_LOAD_RETRY_LIMIT: Final = 1
_COMMAND_TIMEOUT_MS: Final = 30_000


@dataclass(frozen=True, slots=True)
class _CommandStep:
    operation: str
    arguments: tuple[str, ...]
    status: str


def _default_settings() -> QSettings:
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "pATHENA",
        "pATHENA",
    )


def _endpoint(base_url: str) -> tuple[str, int]:
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("LM Studio runtime control requires a loopback HTTP endpoint.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("LM Studio endpoint contains an invalid port.") from exc
    if port is None:
        port = 80
    if not 1 <= port <= 65535:
        raise ValueError("LM Studio endpoint contains an invalid port.")
    bind_host = "::1" if parsed.hostname == "::1" else "127.0.0.1"
    return bind_host, port


def _endpoint_port(base_url: str) -> int:
    """Compatibility helper for tests/callers that only need the validated port."""
    return _endpoint(base_url)[1]


def _find_lms() -> str | None:
    configured = os.environ.get("ATHENA_LMS_EXECUTABLE", "").strip()
    if configured:
        resolved = shutil.which(configured)
        if resolved:
            return resolved
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return str(candidate.resolve(strict=False))
        return None

    candidates = (
        ("lms.exe", "lms", "lms.cmd", "lms.bat")
        if os.name == "nt"
        else ("lms",)
    )
    for executable in candidates:
        resolved = shutil.which(executable)
        if resolved:
            return resolved
    return None


def _safe_cmd_argument(value: str) -> bool:
    if not value or any(character in value for character in "\r\n&|<>^%!"):
        return False
    return True


def _process_command(lms_path: str, arguments: tuple[str, ...]) -> tuple[str, list[str]]:
    suffix = Path(lms_path).suffix.casefold()
    if os.name == "nt" and suffix in {".cmd", ".bat"}:
        values = (lms_path, *arguments)
        if not all(_safe_cmd_argument(value) for value in values):
            raise ValueError("LM Studio command contains unsafe cmd.exe metacharacters.")
        shell = os.environ.get("COMSPEC", "cmd.exe")
        return shell, ["/d", "/s", "/c", lms_path, *arguments]
    return lms_path, list(arguments)


def _should_attempt_auto_load(
    *,
    model_id: str,
    loaded: bool,
    enabled: bool,
    attempted_model_id: str | None,
    busy: bool,
) -> bool:
    """Attempt one automatic load per selected model until the user selects again."""
    return (
        enabled
        and not loaded
        and not busy
        and attempted_model_id != model_id
    )


def _should_attempt_auto_start(
    *,
    provider_ready: bool,
    enabled: bool,
    attempted: bool,
    busy: bool,
) -> bool:
    """Attempt automatic server start once per provider-unavailable episode."""
    return enabled and not provider_ready and not attempted and not busy


def _coerce_idle_minutes(value: object, *, default: int = 30) -> int:
    """Return a bounded persisted idle value without relying on QSettings stub casts."""
    parsed = value if isinstance(value, int) and not isinstance(value, bool) else default
    return max(0, min(1440, parsed))


def _accepted_model_load_id(step: _CommandStep) -> str | None:
    """Return the exact model accepted by a successful model-load command."""
    if (
        step.operation != "model_load"
        or len(step.arguments) < 2
        or step.arguments[0] != "load"
    ):
        return None
    model_id = step.arguments[1].strip()
    return model_id or None


def _model_verification_action(
    *,
    loaded: bool,
    refreshes: int,
    retries: int,
) -> Literal["confirmed", "wait", "retry", "failed"]:
    """Choose the bounded next step after a successful `lms load` command.

    The CLI exit code proves only that the command completed. Core discovery remains
    authoritative for whether the selected model is actually ready.
    """
    if loaded:
        return "confirmed"
    if refreshes < _MODEL_VERIFY_REFRESH_LIMIT:
        return "wait"
    if retries < _MODEL_LOAD_RETRY_LIMIT:
        return "retry"
    return "failed"


class LMStudioRuntimeController(QObject):
    """Start the headless LM Studio service and load the model selected in pATHENA."""

    status_changed = Signal(str)
    busy_changed = Signal(bool)

    def __init__(
        self,
        window: PathenaMainWindow,
        controller: DesktopApiController,
        *,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.controller = controller
        self.settings = settings or _default_settings()
        self.base_url = os.environ.get("ATHENA_LMSTUDIO_BASE_URL", _DEFAULT_BASE_URL).strip()
        self._lms_path = _find_lms()
        self._steps: deque[_CommandStep] = deque()
        self._active_step: _CommandStep | None = None
        self._pending_model_id: str | None = None
        self._auto_load_attempted_model_id: str | None = None
        self._auto_start_attempted = False
        self._verifying_model_id: str | None = None
        self._model_verify_refreshes = 0
        self._model_load_retries = 0
        self._last_snapshot: DesktopApiSnapshot | None = None

        self._model_verify_timer = QTimer(self)
        self._model_verify_timer.setSingleShot(True)
        self._model_verify_timer.setInterval(_MODEL_VERIFY_INTERVAL_MS)
        self._model_verify_timer.timeout.connect(controller.refresh)

        self._command_timer = QTimer(self)
        self._command_timer.setSingleShot(True)
        self._command_timer.setInterval(_COMMAND_TIMEOUT_MS)
        self._command_timer.timeout.connect(self._command_timed_out)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.finished.connect(self._process_finished)
        self.process.errorOccurred.connect(self._process_error)

        self.auto_start = QCheckBox("Start local model server automatically")
        self.auto_load = QCheckBox("Load selected model automatically")
        self.idle_minutes = QSpinBox()
        self.idle_minutes.setRange(0, 1440)
        self.idle_minutes.setSuffix(" min")
        self.idle_minutes.setSpecialValueText("Keep loaded")
        self.idle_minutes.setToolTip(
            "Unload an automatically loaded model after this idle period. "
            "Choose Keep loaded to disable automatic unload."
        )
        self.restart_button = QPushButton("Restart model server")
        self.restart_button.setObjectName("newChatButton")
        self.unload_button = QPushButton("Unload selected model")
        self.unload_button.setObjectName("newChatButton")
        self.runtime_status = QLabel("LM Studio runtime · awaiting Core")
        self.runtime_status.setObjectName("settingsRuntimeDetail")
        self.runtime_status.setWordWrap(True)

        self._restore_settings()
        self._install_settings_panel()

        self.auto_start.toggled.connect(self._auto_start_toggled)
        self.auto_load.toggled.connect(self._auto_load_toggled)
        self.idle_minutes.valueChanged.connect(self._persist_settings)
        self.restart_button.clicked.connect(self.restart_server)
        self.unload_button.clicked.connect(self.unload_selected_model)

        window.model_selector.activated.connect(self._model_selected)
        window.settings_model_selector.activated.connect(self._model_selected)
        controller.snapshot_ready.connect(self.apply_snapshot)
        controller.connection_failed.connect(self._core_failed)

    @property
    def busy(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning or bool(self._steps)

    @property
    def status_text(self) -> str:
        return self.runtime_status.text()

    def _restore_settings(self) -> None:
        self.settings.beginGroup(_SETTINGS_ROOT)
        try:
            auto_start = self.settings.value("auto_start", True, type=bool)
            auto_load = self.settings.value("auto_load", True, type=bool)
            idle_minutes = self.settings.value("idle_minutes", 30, type=int)
        finally:
            self.settings.endGroup()
        self.auto_start.setChecked(bool(auto_start))
        self.auto_load.setChecked(bool(auto_load))
        self.idle_minutes.setValue(_coerce_idle_minutes(idle_minutes))

    @Slot()
    @Slot(bool)
    @Slot(int)
    def _persist_settings(self, _value: object = None) -> None:
        self.settings.beginGroup(_SETTINGS_ROOT)
        try:
            self.settings.setValue("auto_start", self.auto_start.isChecked())
            self.settings.setValue("auto_load", self.auto_load.isChecked())
            self.settings.setValue("idle_minutes", self.idle_minutes.value())
        finally:
            self.settings.endGroup()
        self.settings.sync()

    @Slot(bool)
    def _auto_start_toggled(self, checked: bool) -> None:
        self._persist_settings(checked)
        self._auto_start_attempted = False
        if checked and self._last_snapshot is not None:
            self.apply_snapshot(self._last_snapshot)

    @Slot(bool)
    def _auto_load_toggled(self, checked: bool) -> None:
        self._persist_settings(checked)
        self._model_verify_timer.stop()
        self._verifying_model_id = None
        self._model_verify_refreshes = 0
        self._model_load_retries = 0
        if not checked:
            self._pending_model_id = None
            return
        self._auto_load_attempted_model_id = None
        if self._last_snapshot is not None:
            self.apply_snapshot(self._last_snapshot)

    def _install_settings_panel(self) -> None:
        settings_page = self.window.pages.widget(6)
        if settings_page is None:
            return
        page_layout = settings_page.layout()
        if not isinstance(page_layout, QVBoxLayout):
            return

        panel = QWidget()
        panel.setObjectName("lmStudioRuntimePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Model runtime")
        title.setObjectName("settingsRuntimeTitle")
        layout.addWidget(title)
        layout.addWidget(self.auto_start)
        layout.addWidget(self.auto_load)

        ttl_row = QHBoxLayout()
        ttl_label = QLabel("Idle unload")
        ttl_label.setObjectName("settingsLabel")
        ttl_row.addWidget(ttl_label)
        ttl_row.addStretch(1)
        ttl_row.addWidget(self.idle_minutes)
        layout.addLayout(ttl_row)

        actions = QHBoxLayout()
        actions.addWidget(self.restart_button)
        actions.addWidget(self.unload_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addWidget(self.runtime_status)

        page_layout.addWidget(panel)
        self.panel = panel

    def _set_status(self, message: str) -> None:
        self.runtime_status.setText(message)
        self.runtime_status.setAccessibleDescription(message)
        self.status_changed.emit(message)

    @Slot(object)
    def apply_snapshot(self, value: object) -> None:
        if not isinstance(value, DesktopApiSnapshot):
            return
        self._last_snapshot = value

        provider_ready = (
            value.provider is not None
            and value.provider.status == "ready"
            and value.resolved_model_freshness != "unavailable"
        )
        selected = self.window._selected_model()

        if not provider_ready:
            self.unload_button.setEnabled(False)
            if _should_attempt_auto_start(
                provider_ready=provider_ready,
                enabled=self.auto_start.isChecked(),
                attempted=self._auto_start_attempted,
                busy=self.busy,
            ):
                self._auto_start_attempted = True
                self.ensure_server()
            elif not self.auto_start.isChecked():
                self._set_status("LM Studio runtime · server unavailable")
            return

        self._auto_start_attempted = False

        if selected is None:
            self._pending_model_id = None
            self._auto_load_attempted_model_id = None
            self._model_verify_timer.stop()
            self._verifying_model_id = None
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
            self.unload_button.setEnabled(False)
            self._set_status("LM Studio runtime · server ready · no model selected")
            return

        self.unload_button.setEnabled(selected.loaded and not self.busy)
        if selected.loaded:
            self._pending_model_id = None
            self._model_verify_timer.stop()
            self._verifying_model_id = None
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
            # Remember that this model has been satisfied for the current selection.
            # Keeping this marker avoids immediately undoing an intentional idle-TTL unload.
            self._auto_load_attempted_model_id = selected.backend_model_id
            self._set_status(f"LM Studio runtime · {selected.display_name} loaded")
            return

        if self._verifying_model_id == selected.backend_model_id:
            action = _model_verification_action(
                loaded=selected.loaded,
                refreshes=self._model_verify_refreshes,
                retries=self._model_load_retries,
            )
            if action == "wait":
                self._set_status(
                    f"LM Studio runtime · verifying {selected.display_name} with Core"
                )
                if not self._model_verify_timer.isActive():
                    self._model_verify_refreshes += 1
                    self._model_verify_timer.start()
                return
            if action == "retry":
                self._model_verify_timer.stop()
                self._verifying_model_id = None
                self._model_verify_refreshes = 0
                self._model_load_retries += 1
                self._set_status(
                    f"LM Studio runtime · retrying {selected.display_name} load"
                )
                self.ensure_selected_model()
                return

            self._model_verify_timer.stop()
            self._verifying_model_id = None
            self._pending_model_id = None
            self._model_verify_refreshes = 0
            self._set_status(
                "LM Studio runtime · load completed but Core did not confirm "
                f"{selected.display_name}; reselect the model to retry"
            )
            return

        self._set_status(f"LM Studio runtime · {selected.display_name} available")
        if _should_attempt_auto_load(
            model_id=selected.backend_model_id,
            loaded=selected.loaded,
            enabled=self.auto_load.isChecked(),
            attempted_model_id=self._auto_load_attempted_model_id,
            busy=self.busy,
        ):
            # A newly selected/restored model owns a fresh bounded verification
            # budget. Retries from a prior model must never leak across identities.
            self._model_verify_timer.stop()
            self._verifying_model_id = None
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
            self._pending_model_id = None
            self._auto_load_attempted_model_id = selected.backend_model_id
            self.ensure_selected_model()

    @Slot(str)
    def _core_failed(self, _message: str) -> None:
        self.unload_button.setEnabled(False)
        self._set_status("LM Studio runtime · waiting for local Core")

    @Slot(int)
    def _model_selected(self, _index: int) -> None:
        model = self.window._selected_model()
        self._model_verify_timer.stop()
        self._verifying_model_id = None
        self._model_verify_refreshes = 0
        self._model_load_retries = 0
        self._auto_load_attempted_model_id = None
        self._pending_model_id = None
        if model is None:
            return
        if self.auto_load.isChecked():
            self.ensure_selected_model()

    @Slot()
    def ensure_server(self) -> None:
        if self.busy:
            return
        if self._lms_path is None:
            self._set_status(
                "LM Studio runtime · lms CLI not found; install/enable LM Studio CLI integration"
            )
            return
        try:
            bind_host, port = _endpoint(self.base_url)
        except ValueError as exc:
            self._set_status(f"LM Studio runtime · {exc}")
            return
        self._run_sequence(
            (
                _CommandStep("daemon_up", ("daemon", "up"), "Starting headless LM Studio daemon"),
                _CommandStep(
                    "server_start", ("server", "start", "--port", str(port), "--bind", bind_host),
                    "Starting local LM Studio server",
                ),
            )
        )

    @Slot()
    def restart_server(self) -> None:
        if self.busy:
            return
        self._auto_start_attempted = True
        self._auto_load_attempted_model_id = None
        self._pending_model_id = None
        self._model_verify_timer.stop()
        self._verifying_model_id = None
        self._model_verify_refreshes = 0
        self._model_load_retries = 0
        if self._lms_path is None:
            self._set_status("LM Studio runtime · lms CLI not found")
            return
        try:
            bind_host, port = _endpoint(self.base_url)
        except ValueError as exc:
            self._set_status(f"LM Studio runtime · {exc}")
            return
        self._run_sequence(
            (
                _CommandStep("server_stop", ("server", "stop"), "Stopping local LM Studio server"),
                _CommandStep("daemon_up", ("daemon", "up"), "Ensuring headless LM Studio daemon"),
                _CommandStep(
                    "server_start",
                    ("server", "start", "--port", str(port), "--bind", bind_host),
                    "Starting local LM Studio server",
                ),
            )
        )

    @Slot()
    def ensure_selected_model(self) -> None:
        model = self.window._selected_model()
        if model is None:
            self._pending_model_id = None
            return
        if model.loaded:
            self._pending_model_id = None
            self._model_verify_timer.stop()
            self._verifying_model_id = None
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
            self._set_status(f"LM Studio runtime · {model.display_name} loaded")
            return
        if self.busy:
            return
        if self._lms_path is None:
            self._set_status("LM Studio runtime · lms CLI not found")
            return

        self._auto_load_attempted_model_id = model.backend_model_id
        arguments: list[str] = ["load", model.backend_model_id]
        context = self.window._effective_context_limit()
        if context is not None:
            arguments.extend(("--context-length", str(context)))
        idle_minutes = self.idle_minutes.value()
        if idle_minutes > 0:
            arguments.extend(("--ttl", str(idle_minutes * 60)))

        self._run_sequence(
            (
                _CommandStep(
                    "model_load",
                    tuple(arguments),
                    f"Loading {model.display_name}",
                ),
            )
        )

    @Slot()
    def unload_selected_model(self) -> None:
        model = self.window._selected_model()
        if model is None or not model.loaded or self.busy:
            return
        if self._lms_path is None:
            self._set_status("LM Studio runtime · lms CLI not found")
            return
        self._pending_model_id = None
        self._model_verify_timer.stop()
        self._verifying_model_id = None
        self._model_verify_refreshes = 0
        self._model_load_retries = 0
        # Manual unload must not be immediately reversed by the next Core snapshot.
        self._auto_load_attempted_model_id = model.backend_model_id
        self._run_sequence(
            (
                _CommandStep(
                    "model_unload",
                    ("unload", model.backend_model_id),
                    f"Unloading {model.display_name}",
                ),
            )
        )

    def _run_sequence(self, steps: tuple[_CommandStep, ...]) -> None:
        if self.busy or not steps:
            return
        self._steps.extend(steps)
        self.busy_changed.emit(True)
        self._start_next_step()

    def _start_next_step(self) -> None:
        if not self._steps:
            self._active_step = None
            self.busy_changed.emit(False)
            selected = self.window._selected_model()
            self.unload_button.setEnabled(
                selected is not None and bool(selected.loaded)
            )
            QTimer.singleShot(250, self.controller.refresh)
            return
        if self._lms_path is None:
            self._steps.clear()
            self.busy_changed.emit(False)
            self._set_status("LM Studio runtime · lms CLI not found")
            return

        step = self._steps.popleft()
        self._active_step = step
        self._set_status(f"LM Studio runtime · {step.status} …")
        try:
            program, arguments = _process_command(self._lms_path, step.arguments)
        except ValueError as exc:
            self._steps.clear()
            self._active_step = None
            self.busy_changed.emit(False)
            self._set_status(f"LM Studio runtime · command rejected · {exc}")
            return
        self.process.start(program, arguments)
        self._command_timer.start()

    @Slot()
    def _command_timed_out(self) -> None:
        step = self._active_step
        if step is None:
            return
        self._steps.clear()
        self._active_step = None
        if step.operation == "model_load":
            self._pending_model_id = None
            self._verifying_model_id = None
            self._model_verify_timer.stop()
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
        self.busy_changed.emit(False)
        self._set_status(f"LM Studio runtime · {step.operation} timed out")
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
        QTimer.singleShot(250, self.controller.refresh)

    @Slot(int, QProcess.ExitStatus)
    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        step = self._active_step
        if step is None:
            return
        self._command_timer.stop()
        output = bytes(self.process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        ).strip()

        # A stop/start command can race with an already-correct server state. Refresh
        # after any failure so the Core, rather than CLI wording, decides actual truth.
        if exit_code != 0:
            self._steps.clear()
            self._active_step = None
            self.busy_changed.emit(False)
            if step.operation == "model_load":
                self._pending_model_id = None
                self._verifying_model_id = None
                self._model_verify_timer.stop()
                self._model_verify_refreshes = 0
                self._model_load_retries = 0
            detail = output.splitlines()[-1] if output else f"exit {exit_code}"
            self._set_status(f"LM Studio runtime · {step.operation} failed · {detail}")
            QTimer.singleShot(250, self.controller.refresh)
            return

        if step.operation == "model_load":
            # Exit 0 means LM Studio accepted/completed the load command; only now
            # may the request enter "awaiting Core confirmation" state.
            accepted_model_id = _accepted_model_load_id(step)
            if accepted_model_id is None:
                self._steps.clear()
                self._active_step = None
                self._pending_model_id = None
                self._verifying_model_id = None
                self._model_verify_timer.stop()
                self._model_verify_refreshes = 0
                self._model_load_retries = 0
                self.busy_changed.emit(False)
                self._set_status("LM Studio runtime · invalid model-load command state")
                QTimer.singleShot(250, self.controller.refresh)
                return
            self._pending_model_id = accepted_model_id
            self._verifying_model_id = accepted_model_id
            self._model_verify_refreshes = 0
            self._model_verify_timer.stop()
        self._active_step = None
        self._start_next_step()

    @Slot(QProcess.ProcessError)
    def _process_error(self, error: QProcess.ProcessError) -> None:
        step = self._active_step
        if step is None:
            return
        self._command_timer.stop()
        self._steps.clear()
        self._active_step = None
        self.busy_changed.emit(False)
        label = step.operation if step is not None else "command"
        if step is not None and step.operation == "model_load":
            self._pending_model_id = None
            self._verifying_model_id = None
            self._model_verify_timer.stop()
            self._model_verify_refreshes = 0
            self._model_load_retries = 0
        self._set_status(f"LM Studio runtime · {label} error · {error.name}")
        QTimer.singleShot(250, self.controller.refresh)


def install_lmstudio_runtime(
    window: PathenaMainWindow,
    controller: DesktopApiController,
) -> LMStudioRuntimeController:
    return LMStudioRuntimeController(window, controller)
