"""Live SYSTEM workspace for the native pATHENA desktop shell."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state


class _SystemMetric(QFrame):
    """One compact read-only runtime metric."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self.setObjectName("systemMetric")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)
        heading = QLabel(label)
        heading.setProperty("role", "section")
        self.value = QLabel("—")
        self.value.setObjectName("settingsValue")
        self.value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(heading)
        layout.addWidget(self.value)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class SystemWorkspace(QWidget):
    """Operational view backed by the desktop controller's real API snapshot."""

    def __init__(self, controller: DesktopApiController | None) -> None:
        super().__init__()
        self._controller = controller
        self.setObjectName("systemWorkspace")

        self.core = _SystemMetric("CORE")
        self.provider = _SystemMetric("PROVIDER")
        self.models = _SystemMetric("MODELS")
        self.loaded_models = _SystemMetric("LOADED")
        self.chats = _SystemMetric("CHATS")
        self.api = _SystemMetric("API")
        self.detail = QLabel("Awaiting local Core snapshot.")
        self.detail.setObjectName("systemDetail")
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        set_pathena_ui_state(self.detail, "busy")

        self.refresh_button = QPushButton("REFRESH NOW")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.setToolTip("Refresh local Core, model and chat status")
        self.refresh_button.setEnabled(controller is not None)
        if controller is not None:
            self.refresh_button.clicked.connect(controller.refresh)
            controller.snapshot_ready.connect(self.apply_snapshot)
            controller.connection_failed.connect(self.apply_failure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("LOCAL RUNTIME / SYSTEM")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        intro = QLabel(
            "Live operational state from pATHENA Core and the configured local model "
            "provider. Values refresh with the desktop heartbeat or on demand."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        grid = QGridLayout()
        grid.setContentsMargins(0, 4, 0, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for row, widgets in enumerate(
            (
                (self.core, self.provider, self.api),
                (self.models, self.loaded_models, self.chats),
            )
        ):
            for column, widget in enumerate(widgets):
                grid.addWidget(widget, row, column)
        layout.addLayout(grid)

        detail_heading = QLabel("DETAIL")
        detail_heading.setProperty("role", "section")
        layout.addWidget(detail_heading)
        layout.addWidget(self.detail)
        layout.addStretch(1)

    def apply_snapshot(self, payload: object) -> None:
        if not isinstance(payload, DesktopApiSnapshot):
            return

        provider_status = (
            payload.provider.status if payload.provider is not None else "unavailable"
        )
        loaded = tuple(model for model in payload.models if model.loaded)
        self.core.set_value(payload.health.core_status.upper())
        self.provider.set_value(provider_status.upper())
        self.api.set_value(payload.health.api_version.upper())
        self.models.set_value(str(len(payload.models)))
        self.loaded_models.set_value(str(len(loaded)))
        self.chats.set_value(str(len(payload.chats)))

        detail_parts: list[str] = []
        if payload.health.detail:
            detail_parts.append(payload.health.detail)
        if payload.provider is not None and payload.provider.detail:
            detail_parts.append(payload.provider.detail)
        if payload.model_error:
            detail_parts.append("Model discovery: " + payload.model_error)
        if payload.chat_error:
            detail_parts.append("Chat discovery: " + payload.chat_error)
        if not detail_parts:
            detail_parts.append("Core snapshot is healthy. Local runtime data is current.")
        self.detail.setText("\n".join(detail_parts))

        if payload.model_error or payload.chat_error:
            set_pathena_ui_state(self.detail, "error")
        else:
            set_pathena_ui_state(self.detail, "success")

    def apply_failure(self, message: str) -> None:
        self.core.set_value("DISCONNECTED")
        self.provider.set_value("UNAVAILABLE")
        self.api.set_value("—")
        self.models.set_value("—")
        self.loaded_models.set_value("—")
        self.chats.set_value("—")
        self.detail.setText(message)
        set_pathena_ui_state(self.detail, "error")


def install_system_workspace(
    window: object,
    controller: DesktopApiController | None,
) -> SystemWorkspace:
    """Replace the SYSTEM shell placeholder without widening window.py."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 5:
        raise RuntimeError("pATHENA desktop SYSTEM page is unavailable")

    placeholder = pages.widget(5)
    workspace = SystemWorkspace(controller)
    pages.removeWidget(placeholder)
    pages.insertWidget(5, workspace)
    placeholder.deleteLater()
    return workspace
