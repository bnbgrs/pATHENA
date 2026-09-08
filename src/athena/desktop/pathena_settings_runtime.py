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

from PySide6.QtCore import QObject, QSettings, Qt, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
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

        page_layout.insertWidget(4, self.panel)

    @staticmethod
    def _status_row(name: str, value: QLabel) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)
        label = QLabel(name)
        label.setObjectName("settingsLabel")
        row.addWidget(label)
        row.addStretch(1)
        row.addWidget(value)
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
        freshness = value.resolved_model_freshness
        provider = value.provider
        provider_freshness = "unavailable" if provider is None else freshness

        if provider is None or freshness == "unavailable":
            provider_text = "Model provider · unavailable"
            provider_state = "error"
        elif freshness == "stale":
            provider_text = f"{provider.provider} · last known {provider.status}"
            provider_state = "idle"
        else:
            provider_text = f"{provider.provider} · {provider.status}"
            provider_state = "success" if provider.status == "ready" else "error"
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
        if detail is None and provider is not None:
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