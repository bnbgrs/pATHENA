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
from athena.desktop.system_hardware_acceptance import SystemHardwareAcceptancePanel
from athena.desktop.system_recovery import SystemRecoveryPanel
from athena.desktop.system_runtime_overview import (
    RuntimeFact,
    SystemRuntimeOverview,
    disconnected_system_runtime,
    project_system_runtime,
)


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
        self.storage = _SystemMetric("STORAGE TELEMETRY")
        self.network = _SystemMetric("LOCAL CONNECTIVITY")
        self.hardware_acceptance = SystemHardwareAcceptancePanel()
        self.recovery = SystemRecoveryPanel()
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
                (self.storage, self.network),
            )
        ):
            for column, widget in enumerate(widgets):
                grid.addWidget(widget, row, column)
        layout.addLayout(grid)
        layout.addWidget(self.hardware_acceptance)
        layout.addWidget(self.recovery)

        detail_heading = QLabel("DETAIL")
        detail_heading.setProperty("role", "section")
        layout.addWidget(detail_heading)
        layout.addWidget(self.detail)
        layout.addStretch(1)

    def apply_snapshot(self, payload: object) -> None:
        if not isinstance(payload, DesktopApiSnapshot):
            return
        self._apply_overview(project_system_runtime(payload))

    def apply_failure(self, message: str) -> None:
        self._apply_overview(disconnected_system_runtime(message))

    def _apply_overview(self, overview: SystemRuntimeOverview) -> None:
        for widget, fact in (
            (self.core, overview.core),
            (self.provider, overview.provider),
            (self.api, overview.api),
            (self.models, overview.models),
            (self.loaded_models, overview.loaded_models),
            (self.chats, overview.chats),
            (self.storage, overview.storage),
            (self.network, overview.network),
        ):
            self._apply_fact(widget, fact)
        self.detail.setText(overview.detail)
        set_pathena_ui_state(self.detail, overview.state)

    @staticmethod
    def _apply_fact(widget: _SystemMetric, fact: RuntimeFact) -> None:
        widget.set_value(fact.value)
        presentation_state = {
            "stale": "busy",
            "unavailable": "empty",
        }.get(fact.state, fact.state)
        set_pathena_ui_state(widget.value, presentation_state)


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
