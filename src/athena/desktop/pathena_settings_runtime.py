"""Persistent model settings and honest runtime state for pATHENA Settings.

The extension binds to the existing model controls and ``DesktopApiController``
snapshot.  It does not add provider actions or claim capabilities that the Core
does not report.  Persistence is local, per model and versioned independently
from the backend request contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from typing import Final

from PySide6.QtCore import QObject, QRunnable, QSettings, Qt, QTime, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import NewsProfileResponse
from athena.desktop.api_controller import CoreApiGateway, DesktopApiController, DesktopApiSnapshot
from athena.desktop.pathena_window import PathenaMainWindow

_CORE_READY_STATES: Final = frozenset({"ok", "ready", "running"})
_SETTINGS_ROOT: Final = "desktop/model-settings/v1"


@dataclass(frozen=True, slots=True)
class StoredModelSettings:
    """Validated persisted values; absent or malformed fields remain unset."""

    context_tokens: int | None
    max_output_tokens: int | None
    temperature: float | None
    thinking: bool | None


class _NewsScheduleSignals(QObject):
    loaded = Signal(object)
    saved = Signal(object)
    failed = Signal(str)


class _NewsScheduleTask(QRunnable):
    """Read or update the existing Core-owned News profile off the UI thread."""

    def __init__(
        self,
        gateway: CoreApiGateway,
        *,
        timezone_name: str | None = None,
        local_hour: int | None = None,
        local_minute: int | None = None,
    ) -> None:
        super().__init__()
        self.gateway = gateway
        self.timezone_name = timezone_name
        self.local_hour = local_hour
        self.local_minute = local_minute
        self.signals = _NewsScheduleSignals()

        # Keep the native QRunnable alive until the queued UI delivery releases
        # the controller's Python reference. QThreadPool auto-deletion can race
        # PySide signal delivery on Windows and crash the process.
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        try:
            if self.timezone_name is None:
                profile = self.gateway.news_profile()
                saved = False
            else:
                assert self.local_hour is not None
                assert self.local_minute is not None
                profile = self.gateway.configure_news_schedule(
                    timezone_name=self.timezone_name,
                    local_hour=self.local_hour,
                    local_minute=self.local_minute,
                )
                saved = True
        except Exception as exc:
            self.signals.failed.emit(str(exc) or "News schedule request failed.")
            return
        if saved:
            self.signals.saved.emit(profile)
        else:
            self.signals.loaded.emit(profile)


def model_storage_group(model_id: str) -> str:
    """Return a bounded collision-resistant group for an opaque provider ID."""
    digest = sha256(model_id.encode("utf-8")).hexdigest()
    return f"{_SETTINGS_ROOT}/models/{digest}"


def _positive_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdecimal():
            parsed = int(stripped)
            return parsed if parsed > 0 else None
    return None


def _finite_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if isfinite(parsed) else None


def _boolean(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return None


def _default_settings() -> QSettings:
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "pATHENA",
        "pATHENA",
    )


class SettingsRuntimeController(QObject):
    """Own Settings persistence and render only snapshot-backed runtime facts."""

    def __init__(
        self,
        window: PathenaMainWindow,
        controller: DesktopApiController | None,
        *,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.controller = controller
        self.settings = settings or _default_settings()
        self._hydrating = False
        self._last_snapshot: DesktopApiSnapshot | None = None
        self._news_profile: NewsProfileResponse | None = None
        self._news_task: _NewsScheduleTask | None = None
        self._news_requested = False

        self.panel = QWidget()
        self.panel.setObjectName("settingsRuntimePanel")
        self.provider_value = QLabel("Model provider · awaiting Core")
        self.provider_value.setObjectName("settingsProviderState")
        self.network_value = QLabel("Local Core · awaiting connection")
        self.network_value.setObjectName("settingsNetworkState")
        self.persistence_value = QLabel("Per-model settings · not saved yet")
        self.persistence_value.setObjectName("settingsPersistenceState")
        self.detail = QLabel("Runtime status comes from the local Core API.")
        self.detail.setObjectName("settingsRuntimeDetail")
        self.detail.setWordWrap(True)
        self.news_time = QTimeEdit()
        self.news_time.setObjectName("settingsNewsTime")
        self.news_time.setDisplayFormat("HH:mm")
        self.news_time.setTime(QTime(7, 0))
        self.news_time.setEnabled(False)
        self.news_save = QPushButton("Save schedule")
        self.news_save.setObjectName("settingsNewsScheduleSave")
        self.news_save.setEnabled(False)
        self.news_status = QLabel("News schedule · awaiting Core")
        self.news_status.setObjectName("settingsNewsScheduleState")
        self.news_status.setWordWrap(True)
        self.news_status.setTextFormat(Qt.TextFormat.PlainText)
        for label in (
            self.provider_value,
            self.network_value,
            self.persistence_value,
            self.detail,
        ):
            label.setTextFormat(Qt.TextFormat.PlainText)

        self._set_state(
            self.provider_value,
            self.provider_value.text(),
            "idle",
            freshness="unavailable",
        )
        self._set_state(
            self.network_value,
            self.network_value.text(),
            "idle",
            freshness="unavailable",
        )
        self._set_state(
            self.persistence_value,
            self.persistence_value.text(),
            "idle",
            freshness="unavailable",
        )
        self._set_state(
            self.detail,
            self.detail.text(),
            "idle",
            freshness="unavailable",
        )
        initial_network_detail = (
            "Local Core · awaiting connection. Internet access is not inferred before "
            "a Core snapshot."
        )
        self.network_value.setProperty("pathenaNetworkScope", "unavailable")
        self.network_value.setProperty("pathenaInternetStateInferred", False)
        self.network_value.setToolTip(initial_network_detail)
        self.network_value.setAccessibleDescription(initial_network_detail)

        self._install_panel()
        self._update_settings_copy()

        window.context_spin.valueChanged.connect(self._persist_from_control)
        window.max_output_spin.valueChanged.connect(self._persist_from_control)
        window.temperature_spin.valueChanged.connect(self._persist_from_control)
        window.thinking_checkbox.toggled.connect(self._persist_from_control)
        window.model_selector.activated.connect(self._hydrate_after_selection)
        self.news_save.clicked.connect(self.save_news_schedule)

        if controller is not None:
            controller.snapshot_ready.connect(self.apply_snapshot)
            controller.connection_failed.connect(self.apply_connection_failure)

    def _install_panel(self) -> None:
        settings_page = self.window.pages.widget(6)
        if settings_page is None:
            raise RuntimeError("pATHENA Settings page is unavailable")
        page_layout = settings_page.layout()
        if not isinstance(page_layout, QVBoxLayout):
            raise RuntimeError("pATHENA Settings page has no vertical layout")

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        title = QLabel("Local runtime")
        title.setObjectName("settingsRuntimeTitle")
        layout.addWidget(title)
        layout.addLayout(self._status_row("Provider", self.provider_value))
        layout.addLayout(self._status_row("Connection", self.network_value))
        layout.addLayout(self._status_row("Persistence", self.persistence_value))
        layout.addWidget(self.detail)

        news_title = QLabel("News automation")
        news_title.setObjectName("settingsRuntimeTitle")
        layout.addWidget(news_title)
        news_row = QHBoxLayout()
        news_row.setContentsMargins(0, 0, 0, 0)
        news_row.setSpacing(10)
        news_label = QLabel("Daily update")
        news_label.setObjectName("settingsLabel")
        news_label.setMinimumWidth(84)
        news_row.addWidget(news_label)
        news_row.addWidget(self.news_time)
        news_row.addWidget(self.news_save)
        news_row.addStretch(1)
        layout.addLayout(news_row)
        layout.addWidget(self.news_status)

        page_layout.insertWidget(4, self.panel)

    @staticmethod
    def _status_row(name: str, value: QLabel) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        label = QLabel(name)
        label.setObjectName("settingsLabel")
        label.setMinimumWidth(84)
        value.setWordWrap(True)
        value.setMinimumWidth(0)
        value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )
        row.addWidget(label)
        row.addWidget(value, 1)
        return row

    def _update_settings_copy(self) -> None:
        settings_page = self.window.pages.widget(6)
        if settings_page is None:
            return
        for label in settings_page.findChildren(QLabel, "settingsHelp"):
            if "Settings are kept per model for this session." not in label.text():
                continue
            label.setText(
                label.text().replace(
                    "Settings are kept per model for this session.",
                    "Changes are saved locally per model on this computer.",
                )
            )

    @Slot(object)
    def apply_snapshot(self, value: object) -> None:
        """Render one coherent Core snapshot, then restore the selected model."""
        if not isinstance(value, DesktopApiSnapshot):
            return
        self._last_snapshot = value
        if not self._news_requested:
            self.refresh_news_schedule()
        freshness = value.resolved_model_freshness
        provider = value.provider
        provider_freshness = "unavailable" if provider is None else freshness

        if provider is None:
            provider_text = "Model provider · unavailable"
            provider_state = "error"
        elif freshness == "fresh":
            provider_text = f"{provider.provider} · {provider.status}"
            provider_state = "success" if provider.status == "ready" else "error"
        else:
            provider_text = f"{provider.provider} · last known {provider.status}"
            provider_state = "idle"
        self._set_state(
            self.provider_value,
            provider_text,
            provider_state,
            freshness=provider_freshness,
        )

        core_status = value.health.core_status
        core_ready = core_status in _CORE_READY_STATES
        network_text = (
            "Local Core · connected"
            if core_ready
            else f"Local Core · {core_status}"
        )
        self._set_state(
            self.network_value,
            network_text,
            "success" if core_ready else "error",
            freshness="fresh",
        )
        network_detail = (
            f"{network_text}. Local loopback connection only; this status does not "
            "indicate Internet access."
        )
        self.network_value.setProperty("pathenaNetworkScope", "loopback-only")
        self.network_value.setProperty("pathenaInternetStateInferred", False)
        self.network_value.setToolTip(network_detail)
        self.network_value.setAccessibleDescription(network_detail)

        detail = value.model_error
        if detail is None:
            if provider is None:
                detail = "Model provider is unavailable in the local Core snapshot."
            else:
                detail = provider.detail
        detail_text = (
            detail
            or "Provider readiness is reported by the local Core; no remote status "
            "or unsupported capability is inferred."
        )
        provider_detail_error = (
            provider is None
            or freshness == "unavailable"
            or (
                provider is not None
                and freshness == "fresh"
                and provider.status != "ready"
            )
        )
        self._set_state(
            self.detail,
            detail_text,
            "error" if value.model_error is not None or provider_detail_error else "idle",
            freshness=provider_freshness,
        )
        self.hydrate_selected_model()

    @Slot(str)
    def apply_connection_failure(self, message: str) -> None:
        """Represent a failed Core refresh without retaining a ready claim."""
        self._set_state(
            self.provider_value,
            "Model provider · unavailable",
            "error",
            freshness="unavailable",
        )
        self._set_state(
            self.network_value,
            "Local Core · unavailable",
            "error",
            freshness="unavailable",
        )
        network_detail = (
            "Local Core unavailable. Internet-access state is not inferred from this "
            "failed local connection."
        )
        self.network_value.setProperty("pathenaNetworkScope", "unavailable")
        self.network_value.setProperty("pathenaInternetStateInferred", False)
        self.network_value.setToolTip(network_detail)
        self.network_value.setAccessibleDescription(network_detail)
        self._set_state(
            self.detail,
            message,
            "error",
            freshness="unavailable",
        )

    def refresh_news_schedule(self) -> None:
        controller = self.controller
        if controller is None or self._news_task is not None:
            return
        gateway = getattr(controller, "gateway", None)
        if gateway is None or not hasattr(gateway, "news_profile"):
            return
        self._news_requested = True
        self.news_status.setText("News schedule · loading…")
        task = _NewsScheduleTask(gateway)
        task.signals.loaded.connect(self.apply_news_profile)
        task.signals.failed.connect(self._apply_news_failure)
        self._news_task = task
        controller.thread_pool.start(task)

    @Slot()
    def save_news_schedule(self) -> None:
        controller = self.controller
        profile = self._news_profile
        if controller is None or profile is None or self._news_task is not None:
            return
        gateway = getattr(controller, "gateway", None)
        if gateway is None or not hasattr(gateway, "configure_news_schedule"):
            return
        value = self.news_time.time()
        self.news_save.setEnabled(False)
        self.news_status.setText("News schedule · saving…")
        task = _NewsScheduleTask(
            gateway,
            timezone_name=profile.timezone_name,
            local_hour=value.hour(),
            local_minute=value.minute(),
        )
        task.signals.saved.connect(self.apply_news_profile)
        task.signals.failed.connect(self._apply_news_failure)
        self._news_task = task
        controller.thread_pool.start(task)

    @Slot(object)
    def apply_news_profile(self, value: object) -> None:
        if not isinstance(value, NewsProfileResponse):
            self._apply_news_failure("Core returned an invalid News profile.")
            return
        self._news_task = None
        self._news_profile = value
        self.news_time.setTime(QTime(value.local_hour, value.local_minute))
        self.news_time.setEnabled(True)
        self.news_save.setEnabled(True)
        state = "enabled" if value.enabled else "disabled"
        self.news_status.setText(
            f"News {state} · daily {value.local_hour:02d}:{value.local_minute:02d} · "
            f"{value.timezone_name}"
        )
        self.news_status.setProperty("pathenaUiState", "success" if value.enabled else "idle")
        self.news_status.setAccessibleDescription(self.news_status.text())

    @Slot(str)
    def _apply_news_failure(self, message: str) -> None:
        self._news_task = None
        self.news_status.setText(f"News schedule unavailable · {message}")
        self.news_status.setProperty("pathenaUiState", "error")
        self.news_status.setAccessibleDescription(self.news_status.text())
        self.news_save.setEnabled(self._news_profile is not None)
        self.news_time.setEnabled(self._news_profile is not None)

    @staticmethod
    def _set_state(
        label: QLabel,
        text: str,
        ui_state: str,
        *,
        freshness: str,
    ) -> None:
        label.setText(text)
        label.setProperty("pathenaUiState", ui_state)
        label.setProperty("pathenaRuntimeFreshness", freshness)
        label.setAccessibleDescription(text)

    @Slot(int)
    @Slot(float)
    @Slot(bool)
    def _persist_from_control(self, _value: object) -> None:
        self.persist_selected_model()

    @Slot(int)
    def _hydrate_after_selection(self, _index: int) -> None:
        self.hydrate_selected_model()

    def persist_selected_model(self) -> None:
        """Synchronously persist the controls already used for real requests."""
        if self._hydrating:
            return
        model = self.window._selected_model()
        if model is None:
            return

        group = model_storage_group(model.backend_model_id)
        self.settings.beginGroup(group)
        try:
            self.settings.remove("")
            self.settings.setValue("model_id", model.backend_model_id)
            runtime_limit = model.loaded_context_length or model.context_capacity
            if runtime_limit is not None:
                self.settings.setValue("context_tokens", self.window.context_spin.value())
            self.settings.setValue(
                "max_output_tokens",
                self.window.max_output_spin.value(),
            )
            self.settings.setValue(
                "temperature",
                float(self.window.temperature_spin.value()),
            )
            self.settings.setValue(
                "thinking",
                self.window.thinking_checkbox.isChecked(),
            )
        finally:
            self.settings.endGroup()
        self.settings.sync()

        if self.settings.status() == QSettings.Status.NoError:
            self._set_state(
                self.persistence_value,
                f"{model.display_name} · saved locally",
                "success",
                freshness="fresh",
            )
            return
        self._set_state(
            self.persistence_value,
            f"{model.display_name} · local save failed",
            "error",
            freshness="unavailable",
        )

    def hydrate_selected_model(self) -> None:
        """Restore validated values through the existing control handlers."""
        model = self.window._selected_model()
        if model is None:
            self._set_state(
                self.persistence_value,
                "Per-model settings · choose a model",
                "idle",
                freshness="unavailable",
            )
            return
        stored = self._read_model(
            model.backend_model_id,
            display_name=model.display_name,
        )
        if stored is None:
            if self.settings.status() != QSettings.Status.NoError:
                return
            self._set_state(
                self.persistence_value,
                f"{model.display_name} · defaults not yet saved",
                "idle",
                freshness="unavailable",
            )
            return
        if all(
            value is None
            for value in (
                stored.context_tokens,
                stored.max_output_tokens,
                stored.temperature,
                stored.thinking,
            )
        ):
            self._set_state(
                self.persistence_value,
                f"{model.display_name} · invalid local values; defaults kept",
                "error",
                freshness="unavailable",
            )
            return

        self._hydrating = True
        try:
            runtime_limit = model.loaded_context_length or model.context_capacity
            if stored.context_tokens is not None and runtime_limit is not None:
                context = max(
                    self.window.context_spin.minimum(),
                    min(stored.context_tokens, self.window.context_spin.maximum()),
                )
                self.window.context_spin.setValue(context)
            if stored.max_output_tokens is not None:
                output = max(
                    self.window.max_output_spin.minimum(),
                    min(
                        stored.max_output_tokens,
                        self.window.max_output_spin.maximum(),
                    ),
                )
                self.window.max_output_spin.setValue(output)
            if stored.temperature is not None:
                temperature = max(
                    self.window.temperature_spin.minimum(),
                    min(stored.temperature, self.window.temperature_spin.maximum()),
                )
                self.window.temperature_spin.setValue(temperature)
            if stored.thinking is not None:
                self.window.thinking_checkbox.setChecked(stored.thinking)
        finally:
            self._hydrating = False

        self._set_state(
            self.persistence_value,
            f"{model.display_name} · restored locally",
            "success",
            freshness="fresh",
        )

    def _read_model(
        self,
        model_id: str,
        *,
        display_name: str,
    ) -> StoredModelSettings | None:
        group = model_storage_group(model_id)
        self.settings.beginGroup(group)
        try:
            if str(self.settings.value("model_id", "")) != model_id:
                return None
            context = _positive_int(self.settings.value("context_tokens"))
            output = _positive_int(self.settings.value("max_output_tokens"))
            temperature = _finite_float(self.settings.value("temperature"))
            thinking = _boolean(self.settings.value("thinking"))
        finally:
            self.settings.endGroup()
        if self.settings.status() != QSettings.Status.NoError:
            self._set_state(
                self.persistence_value,
                f"{display_name} · local settings unreadable",
                "error",
                freshness="unavailable",
            )
            return None
        return StoredModelSettings(
            context_tokens=context,
            max_output_tokens=output,
            temperature=temperature,
            thinking=thinking,
        )


def install_settings_runtime(
    window: PathenaMainWindow,
    controller: DesktopApiController | None,
    *,
    settings: QSettings | None = None,
) -> SettingsRuntimeController:
    """Install OPS-001 without changing shared shell or backend contracts."""
    runtime = SettingsRuntimeController(window, controller, settings=settings)
    window.setProperty("pathenaSettingsRuntimeController", runtime)
    window.setProperty("pathenaSettingsPersistenceEnabled", True)
    return runtime