"""Live SYSTEM workspace for the native pATHENA desktop shell."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QHideEvent, QShowEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.pathena_system_tray import install_system_tray
from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state
from athena.desktop.system_hardware_acceptance import SystemHardwareAcceptancePanel
from athena.desktop.system_recovery import SystemRecoveryPanel
from athena.desktop.system_runtime_overview import (
    RuntimeFact,
    SystemRuntimeOverview,
    disconnected_system_runtime,
    project_system_runtime,
)


def _presentation_state(state: str) -> str:
    """Map truthful runtime vocabulary onto the shared UI-state vocabulary."""
    return {
        "stale": "busy",
        "unavailable": "empty",
    }.get(state, state)


class _SystemStatusRow(QFrame):
    """One major SYSTEM status row in the reference composition."""

    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        self.setObjectName("systemStatusRow")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(82)
        self.setAccessibleName(title)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 14, 14)
        layout.setSpacing(14)

        self.icon = QLabel("○")
        self.icon.setObjectName("systemStatusIcon")
        self.icon.setFixedWidth(28)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(4)
        heading = QLabel(title)
        heading.setObjectName("systemStatusTitle")
        self.description = QLabel(description)
        self.description.setObjectName("settingsHelp")
        self.description.setWordWrap(True)
        copy.addWidget(heading)
        copy.addWidget(self.description)

        self.value = QLabel("Awaiting snapshot")
        self.value.setObjectName("settingsValue")
        self.value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        layout.addWidget(self.icon)
        layout.addLayout(copy, 1)
        layout.addWidget(self.value)

    def set_fact(self, fact: RuntimeFact, *, description: str | None = None) -> None:
        self.value.setText(fact.value)
        if description is not None:
            self.description.setText(description)
        state = _presentation_state(fact.state)
        set_pathena_ui_state(self, state)
        set_pathena_ui_state(self.icon, state)
        set_pathena_ui_state(self.value, state)


class _PostureRow(QWidget):
    """Truthful read-only security posture row."""

    def __init__(self, title: str) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)
        label = QLabel(title)
        label.setObjectName("settingsLabel")
        self.value = QLabel("Unavailable")
        self.value.setObjectName("settingsValue")
        self.value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(self.value)

    def set_fact(self, fact: RuntimeFact) -> None:
        self.value.setText(fact.value)
        set_pathena_ui_state(self.value, _presentation_state(fact.state))


class _SystemSubnav(QFrame):
    """Reference secondary navigation without inventing backend destinations."""

    ITEMS = ("Overview", "Runtime", "Storage", "Network", "Logs")

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("systemSubnav")
        self.setAccessibleName("System sections")
        self.setFixedWidth(218)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 22, 0)
        layout.setSpacing(4)

        section = QLabel("SYSTEM")
        section.setObjectName("sessionLabel")
        layout.addWidget(section)
        layout.addSpacing(8)

        for index, text in enumerate(self.ITEMS):
            item = QLabel(text)
            item.setObjectName("systemSubnavItem")
            item.setProperty("selected", index == 0)
            item.setAccessibleName(f"System section: {text}")
            if index == 0:
                item.setText("●  Overview")
                item.setAccessibleDescription("Current System overview")
            else:
                item.setText(f"   {text}  ·  Unavailable")
                item.setProperty("pathenaUnavailable", True)
                item.setAccessibleDescription(
                    f"{text} section unavailable in this build"
                )
                set_pathena_ui_state(item, "empty")
            layout.addWidget(item)
        layout.addStretch(1)


class _SecurityPosture(QFrame):
    """Reference right-side posture panel using only snapshot-backed facts."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("systemSecurityPosture")
        self.setAccessibleName("Security posture")
        self.setFixedWidth(348)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 8, 0, 0)
        layout.setSpacing(8)

        heading = QLabel("Security posture")
        heading.setObjectName("inspectorHeading")
        layout.addWidget(heading)

        note = QLabel(
            "Only states exposed by the local Core snapshot are asserted. "
            "Missing security telemetry remains unavailable."
        )
        note.setObjectName("settingsHelp")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addSpacing(8)

        self.loopback = _PostureRow("Loopback only")
        self.local_processing = _PostureRow("Local processing")
        self.encrypted = _PostureRow("Encrypted at rest")
        self.tor = _PostureRow("Tor status")
        for row in (self.loopback, self.local_processing, self.encrypted, self.tor):
            layout.addWidget(row)

        layout.addStretch(1)

    def apply(self, overview: SystemRuntimeOverview) -> None:
        self.loopback.set_fact(overview.loopback)
        self.local_processing.set_fact(overview.local_processing)
        self.encrypted.set_fact(overview.encrypted_at_rest)
        self.tor.set_fact(overview.tor)


class SystemWorkspace(QWidget):
    """Operational view backed by the desktop controller's real API snapshot."""

    def __init__(self, controller: DesktopApiController | None) -> None:
        super().__init__()
        self._controller = controller
        self._shell_inspector: QFrame | None = None
        self.setObjectName("systemWorkspace")

        self.runtime = _SystemStatusRow(
            "Local runtime",
            "Core availability, API version and local model-provider state.",
        )
        self.storage = _SystemStatusRow(
            "Knowledge storage",
            "Read-only storage health from the Core when that probe is available.",
        )
        self.connectivity = _SystemStatusRow(
            "Connectivity",
            "Reachability of the configured local model-provider boundary.",
        )
        self.background = _SystemStatusRow(
            "Background work",
            "Queue and maintenance activity when exposed by the Core snapshot.",
        )
        self.security_posture = _SecurityPosture()
        self.hardware_acceptance = SystemHardwareAcceptancePanel()
        self.recovery = SystemRecoveryPanel()

        self.recent_events = QLabel(
            "Event history is unavailable — the current desktop snapshot exposes no "
            "durable activity feed."
        )
        self.recent_events.setObjectName("systemRecentEventsEmpty")
        self.recent_events.setWordWrap(True)
        set_pathena_ui_state(self.recent_events, "empty")

        self.detail = QLabel("Awaiting local Core snapshot.")
        self.detail.setObjectName("systemDetail")
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        set_pathena_ui_state(self.detail, "busy")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.setToolTip("Refresh local Core, model and chat status")
        self.refresh_button.setAccessibleName("Refresh System status")
        self.refresh_button.setEnabled(controller is not None)
        if controller is not None:
            self.refresh_button.clicked.connect(controller.refresh)
            controller.snapshot_ready.connect(self.apply_snapshot)
            controller.connection_failed.connect(self.apply_failure)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(8, 0, 18, 28)
        outer.setSpacing(0)
        outer.addWidget(_SystemSubnav())

        main = QWidget()
        main.setObjectName("systemMain")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(28, 0, 26, 0)
        main_layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("System")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        main_layout.addLayout(header)

        intro = QLabel(
            "Operational state from pATHENA Core. Missing probes stay explicitly "
            "unavailable rather than being inferred by the desktop."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        main_layout.addWidget(intro)
        main_layout.addSpacing(6)

        for row in (
            self.runtime,
            self.storage,
            self.connectivity,
            self.background,
        ):
            main_layout.addWidget(row)

        main_layout.addSpacing(8)
        events_heading = QLabel("Recent events")
        events_heading.setProperty("role", "section")
        main_layout.addWidget(events_heading)
        main_layout.addWidget(self.recent_events)

        main_layout.addSpacing(8)
        diagnostics_heading = QLabel("Diagnostics")
        diagnostics_heading.setProperty("role", "section")
        main_layout.addWidget(diagnostics_heading)
        main_layout.addWidget(self.hardware_acceptance)
        main_layout.addWidget(self.recovery)
        main_layout.addWidget(self.detail)
        main_layout.addStretch(1)

        outer.addWidget(main, 1)
        outer.addWidget(self.security_posture)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._hide_shell_inspector()
        QTimer.singleShot(0, self._hide_shell_inspector)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        if self._shell_inspector is not None:
            self._shell_inspector.show()
            self._shell_inspector = None
        super().hideEvent(event)

    def _hide_shell_inspector(self) -> None:
        inspector = self.window().findChild(QFrame, "inspector")
        if inspector is None:
            return
        self._shell_inspector = inspector
        inspector.hide()

    def apply_snapshot(self, payload: object) -> None:
        if not isinstance(payload, DesktopApiSnapshot):
            return
        self._apply_overview(project_system_runtime(payload))

    def apply_failure(self, message: str) -> None:
        self._apply_overview(disconnected_system_runtime(message))

    def _apply_overview(self, overview: SystemRuntimeOverview) -> None:
        self.runtime.set_fact(
            overview.core,
            description=(
                f"API {overview.api.value} · Provider {overview.provider.value} · "
                f"{overview.models.value} models · {overview.chats.value} chats"
            ),
        )
        self.storage.set_fact(overview.storage)
        self.connectivity.set_fact(overview.network)
        self.background.set_fact(overview.background)
        self.security_posture.apply(overview)
        self.detail.setText(overview.detail)
        set_pathena_ui_state(self.detail, _presentation_state(overview.state))

        tray_controller = getattr(
            self.window(), "_pathena_system_tray_controller", None
        )
        apply_runtime_state = getattr(tray_controller, "apply_runtime_state", None)
        if callable(apply_runtime_state):
            apply_runtime_state(overview.state)


def install_system_workspace(
    window: object,
    controller: DesktopApiController | None,
) -> SystemWorkspace:
    """Replace SYSTEM placeholder and own the desktop tray lifecycle."""
    if not isinstance(window, QWidget):
        raise RuntimeError("pATHENA desktop SYSTEM page requires a QWidget window")
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 5:
        raise RuntimeError("pATHENA desktop SYSTEM page is unavailable")

    placeholder = pages.widget(5)
    workspace = SystemWorkspace(controller)
    pages.removeWidget(placeholder)
    pages.insertWidget(5, workspace)
    placeholder.deleteLater()

    if getattr(window, "_pathena_system_tray_controller", None) is None:
        window._pathena_system_tray_controller = install_system_tray(window)  # type: ignore[attr-defined]
    return workspace
