"""Reusable presentation primitives for the pATHENA v2 desktop UI.

These widgets intentionally contain no domain, persistence or provider logic.
They exist so every workspace shares the same interaction and visual grammar.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class V2NavigationButton(QPushButton):
    """Primary navigation action with one explicit active-state contract."""

    def __init__(self, text: str, *, accessible_name: str | None = None) -> None:
        super().__init__(text)
        self.setProperty("v2Nav", True)
        self.setProperty("active", False)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(40)
        self.setAccessibleName(accessible_name or f"Open {text}")

    def set_active(self, active: bool) -> None:
        """Update the dynamic property and repaint only when state changed."""
        if bool(self.property("active")) == active:
            return
        self.setProperty("active", active)
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()


class V2WorkspaceHeader(QFrame):
    """Shared top header for every primary workspace."""

    def __init__(self, title: str, hint: str) -> None:
        super().__init__()
        self.setObjectName("v2Header")
        self.setFixedHeight(74)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 12, 22, 12)
        layout.setSpacing(12)

        title_stack = QVBoxLayout()
        title_stack.setContentsMargins(0, 0, 0, 0)
        title_stack.setSpacing(1)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("v2PageTitle")
        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("v2PageHint")

        title_stack.addWidget(self.title_label)
        title_stack.addWidget(self.hint_label)
        layout.addLayout(title_stack)
        layout.addStretch(1)

        self.action_host = QFrame()
        self.action_host.setObjectName("v2HeaderActions")
        self.action_layout = QHBoxLayout(self.action_host)
        self.action_layout.setContentsMargins(0, 0, 0, 0)
        self.action_layout.setSpacing(10)
        layout.addWidget(self.action_host)

    def set_context(self, title: str, hint: str) -> None:
        self.title_label.setText(title)
        self.hint_label.setText(hint)


class V2Surface(QFrame):
    """Neutral content surface for bounded controls or master/detail regions."""

    def __init__(self, *, object_name: str = "v2Surface") -> None:
        super().__init__()
        self.setObjectName(object_name)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class V2InspectorHost(QFrame):
    """Contextual secondary pane with a stable visibility contract."""

    def __init__(self, *, width: int = 348) -> None:
        super().__init__()
        self.setObjectName("v2InspectorHost")
        self.setFixedWidth(width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._content: QWidget | None = None
        self.hide()

    @property
    def content(self) -> QWidget | None:
        return self._content

    def set_content(self, widget: QWidget) -> None:
        if self._content is widget:
            return
        if self._content is not None:
            self._layout.removeWidget(self._content)
            self._content.setParent(None)
        self._content = widget
        widget.setParent(self)
        self._layout.addWidget(widget)

    def set_open(self, visible: bool) -> None:
        self.setVisible(visible and self._content is not None)


class V2SectionLabel(QLabel):
    """Small metadata heading used inside compact toolbars and forms."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("v2Eyebrow")


class V2EmptyState(QFrame):
    """Simple reusable zero-state without card-grid decoration."""

    def __init__(self, title: str, body: str) -> None:
        super().__init__()
        self.setObjectName("v2EmptyState")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(8)
        layout.addStretch(1)

        heading = QLabel(title)
        heading.setObjectName("v2EmptyTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)

        description = QLabel(body)
        description.setObjectName("v2EmptyBody")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setMaximumWidth(520)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(description)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(1)
