"""Reusable presentation primitives for the pATHENA v2 desktop UI.

These widgets intentionally contain no domain, persistence or provider logic.
They exist so every workspace shares the same interaction and visual grammar.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QCursor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

_NAV_ICON_COLORS = {
    False: QColor("#8793AA"),
    True: QColor("#A99FFF"),
}


def _navigation_icon(name: str, *, active: bool) -> QIcon:
    """Draw one crisp, dependency-free navigation glyph for the desktop rail."""
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(_NAV_ICON_COLORS[active], 1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == "chat":
        painter.drawRoundedRect(QRectF(2.5, 3.0, 15.0, 11.5), 3.0, 3.0)
        painter.drawLine(QPointF(6.0, 14.5), QPointF(4.5, 17.0))
        painter.drawLine(QPointF(6.0, 14.5), QPointF(9.0, 14.5))
    elif name == "knowledge":
        painter.drawRoundedRect(QRectF(3.0, 2.5, 6.4, 14.5), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(10.6, 2.5, 6.4, 14.5), 1.5, 1.5)
        painter.drawLine(QPointF(10.0, 4.0), QPointF(10.0, 16.0))
    elif name == "research":
        painter.drawEllipse(QRectF(3.0, 3.0, 10.5, 10.5))
        painter.drawLine(QPointF(12.0, 12.0), QPointF(17.0, 17.0))
        painter.drawLine(QPointF(6.0, 8.2), QPointF(10.5, 8.2))
    elif name == "jobs":
        painter.drawRoundedRect(QRectF(2.5, 4.5, 15.0, 12.5), 2.0, 2.0)
        painter.drawRoundedRect(QRectF(7.0, 2.5, 6.0, 3.5), 1.2, 1.2)
        painter.drawLine(QPointF(2.8, 9.5), QPointF(17.2, 9.5))
        painter.drawLine(QPointF(8.5, 9.5), QPointF(11.5, 9.5))
    elif name == "sources":
        painter.drawRoundedRect(QRectF(4.0, 2.5, 12.0, 15.0), 1.5, 1.5)
        painter.drawLine(QPointF(7.0, 7.0), QPointF(13.0, 7.0))
        painter.drawLine(QPointF(7.0, 10.0), QPointF(13.0, 10.0))
        painter.drawLine(QPointF(7.0, 13.0), QPointF(11.0, 13.0))
    elif name == "pallas":
        painter.drawEllipse(QRectF(2.5, 7.0, 5.0, 5.0))
        painter.drawEllipse(QRectF(12.5, 2.5, 5.0, 5.0))
        painter.drawEllipse(QRectF(12.5, 12.5, 5.0, 5.0))
        painter.drawLine(QPointF(7.5, 8.5), QPointF(12.5, 6.0))
        painter.drawLine(QPointF(7.5, 10.5), QPointF(12.5, 14.0))
    elif name == "system":
        painter.drawEllipse(QRectF(2.5, 2.5, 15.0, 15.0))
        painter.drawLine(QPointF(10.0, 10.0), QPointF(14.5, 6.5))
        painter.drawEllipse(QRectF(8.8, 8.8, 2.4, 2.4))
        painter.drawLine(QPointF(5.0, 14.2), QPointF(15.0, 14.2))
    elif name == "settings":
        for y, knob_x in ((4.5, 7.0), (10.0, 13.0), (15.5, 9.0)):
            painter.drawLine(QPointF(3.0, y), QPointF(17.0, y))
            painter.drawEllipse(QRectF(knob_x - 1.8, y - 1.8, 3.6, 3.6))

    painter.end()
    return QIcon(pixmap)


class V2NavigationButton(QPushButton):
    """Primary navigation action with one explicit active-state contract."""

    def __init__(
        self,
        text: str,
        *,
        icon_name: str,
        accessible_name: str | None = None,
    ) -> None:
        super().__init__(text)
        self._icons = {
            False: _navigation_icon(icon_name, active=False),
            True: _navigation_icon(icon_name, active=True),
        }
        self.setProperty("v2Nav", True)
        self.setProperty("active", False)
        self.setIcon(self._icons[False])
        self.setIconSize(QSize(18, 18))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(40)
        self.setAccessibleName(accessible_name or f"Open {text}")

    def set_active(self, active: bool) -> None:
        """Update the dynamic property and repaint only when state changed."""
        if bool(self.property("active")) == active:
            return
        self.setProperty("active", active)
        self.setIcon(self._icons[active])
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


class V2FormRow(QFrame):
    """Label, explanation and one real control region for admin workspaces."""

    def __init__(self, title: str, description: str = "") -> None:
        super().__init__()
        self.setObjectName("v2FormRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 14, 0, 14)
        layout.setSpacing(24)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(3)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("v2FormLabel")
        copy.addWidget(self.title_label)

        self.description_label = QLabel(description)
        self.description_label.setObjectName("v2FormDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(bool(description))
        copy.addWidget(self.description_label)

        layout.addLayout(copy, 1)

        self.control_host = QFrame()
        self.control_host.setObjectName("v2FormControl")
        self.control_layout = QHBoxLayout(self.control_host)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(8)
        self.control_host.setMinimumWidth(320)
        layout.addWidget(self.control_host)

    def add_control(self, widget: QWidget, stretch: int = 0) -> None:
        widget.setParent(self.control_host)
        self.control_layout.addWidget(widget, stretch)
