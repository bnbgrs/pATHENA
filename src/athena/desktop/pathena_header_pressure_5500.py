"""Compact-width header pressure relief for existing pATHENA actions.

At the supported minimum desktop width, chat selectors and multi-action workspace
headers can compete with primary content. This presentation-only controller reduces
padding and selector minimum widths in compact mode. It never shortens labels, removes
actions, changes order or invokes a command.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QComboBox, QPushButton, QSizePolicy, QWidget

_COMPACT_THRESHOLD = 1460

_ACTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("researchWorkspace", ("start_button", "refresh_button", "cancel_button")),
    (
        "jobsWorkspace",
        (
            "refresh_button",
            "pause_button",
            "resume_button",
            "wake_button",
            "cancel_button",
        ),
    ),
    ("filesWorkspace", ("import_button", "refresh_button", "process_button")),
    (
        "backupWorkspace",
        (
            "refresh_button",
            "create_button",
            "targets_button",
            "register_target_button",
            "verify_button",
            "deep_verify_button",
            "restore_button",
        ),
    ),
)

_HEADER_STYLESHEET = """
/* pATHENA compact header pressure relief */
QPushButton[pathenaCompactHeaderAction="true"] {
    padding: 4px 7px;
}
"""


class HeaderPressureController(QObject):
    """Reduce header chrome at compact widths without reducing capability."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._actions: tuple[QPushButton, ...] = self._resolve_actions()
        self.chat_selector: object = getattr(window, "chat_selector", None)
        self.model_selector: object = getattr(window, "model_selector", None)
        window.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self.sync()
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        compact = self.window.width() <= _COMPACT_THRESHOLD
        for button in self._actions:
            changed = bool(button.property("pathenaCompactHeaderAction")) != compact
            button.setProperty("pathenaCompactHeaderAction", compact)
            button.setProperty("pathenaHeaderCapabilityPreserved", True)
            policy = button.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Policy.Minimum)
            button.setSizePolicy(policy)
            if changed:
                style = button.style()
                style.unpolish(button)
                style.polish(button)
                button.update()

        self._tune_selector(
            self.chat_selector,
            compact,
            compact_width=180,
            regular=220,
        )
        self._tune_selector(
            self.model_selector,
            compact,
            compact_width=160,
            regular=190,
        )
        self.window.setProperty(
            "pathenaHeaderPressureMode",
            "compact" if compact else "regular",
        )

    @staticmethod
    def _tune_selector(
        candidate: object,
        compact: bool,
        *,
        compact_width: int,
        regular: int,
    ) -> None:
        if not isinstance(candidate, QComboBox):
            return
        candidate.setMinimumWidth(compact_width if compact else regular)
        candidate.setProperty("pathenaCompactHeaderSelector", compact)
        candidate.setProperty("pathenaHeaderCapabilityPreserved", True)

    def _resolve_actions(self) -> tuple[QPushButton, ...]:
        actions: list[QPushButton] = []
        for workspace_name, attributes in _ACTIONS:
            workspace = self.window.findChild(QWidget, workspace_name)
            if workspace is None:
                continue
            for attribute in attributes:
                candidate = getattr(workspace, attribute, None)
                if isinstance(candidate, QPushButton):
                    actions.append(candidate)
        for attribute in ("new_chat_button", "delete_chat_button"):
            candidate = getattr(self.window, attribute, None)
            if isinstance(candidate, QPushButton):
                actions.append(candidate)
        return tuple(actions)


def apply_ui_refinements_5401_5500(window: QWidget) -> tuple[int, ...]:
    """Install compact header relief without hiding or renaming actions."""
    controller = HeaderPressureController(window)
    if _HEADER_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_HEADER_STYLESHEET}")
    window.setProperty("pathenaHeaderPressureController", controller)
    window.setProperty("pathenaHeaderPressureManaged", True)
    return tuple(range(5401, 5501))
