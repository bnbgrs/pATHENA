"""Presentation primitives for the pATHENA V3 living workspace.

V3 deliberately owns its visual grammar. Domain state, persistence and provider
behavior remain outside this module.
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
    QToolButton,
    QVBoxLayout,
    QWidget,
)

_INK = QColor("#F2F0E8")
_MUTED = QColor("#817F77")
_ACTIVE = QColor("#C6F277")


def _glyph_icon(name: str, *, active: bool) -> QIcon:
    """Draw dependency-free V3 navigation glyphs."""

    pixmap = QPixmap(22, 22)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(_ACTIVE if active else _MUTED, 1.75)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == "chat":
        painter.drawRoundedRect(QRectF(3, 4, 16, 12), 4, 4)
        painter.drawLine(QPointF(7, 16), QPointF(5.5, 19))
        painter.drawLine(QPointF(7, 16), QPointF(10, 16))
    elif name == "knowledge":
        painter.drawRoundedRect(QRectF(4, 3, 6, 16), 2, 2)
        painter.drawRoundedRect(QRectF(12, 3, 6, 16), 2, 2)
        painter.drawLine(QPointF(11, 5), QPointF(11, 18))
    elif name == "research":
        painter.drawEllipse(QRectF(3.5, 3.5, 11, 11))
        painter.drawLine(QPointF(13, 13), QPointF(18.5, 18.5))
        painter.drawLine(QPointF(7, 9), QPointF(11.5, 9))
    elif name == "jobs":
        painter.drawRoundedRect(QRectF(3, 5, 16, 13), 3, 3)
        painter.drawRoundedRect(QRectF(8, 3, 6, 4), 1.5, 1.5)
        painter.drawLine(QPointF(3.5, 10.5), QPointF(18.5, 10.5))
    elif name == "sources":
        painter.drawRoundedRect(QRectF(5, 2.5, 12, 17), 2, 2)
        painter.drawLine(QPointF(8, 7), QPointF(14, 7))
        painter.drawLine(QPointF(8, 10.5), QPointF(14, 10.5))
        painter.drawLine(QPointF(8, 14), QPointF(12, 14))
    elif name == "pallas":
        painter.drawEllipse(QRectF(2.5, 8, 5, 5))
        painter.drawEllipse(QRectF(13.5, 3, 5, 5))
        painter.drawEllipse(QRectF(13.5, 14, 5, 5))
        painter.drawLine(QPointF(7.5, 9.5), QPointF(13.5, 6))
        painter.drawLine(QPointF(7.5, 11.5), QPointF(13.5, 16.5))
    elif name == "system":
        painter.drawEllipse(QRectF(3, 3, 16, 16))
        painter.drawLine(QPointF(11, 11), QPointF(15.5, 7))
        painter.drawEllipse(QRectF(9.8, 9.8, 2.4, 2.4))
        painter.drawLine(QPointF(6, 16), QPointF(16, 16))
    elif name == "settings":
        for y, knob_x in ((5, 8), (11, 15), (17, 10)):
            painter.drawLine(QPointF(4, y), QPointF(18, y))
            painter.drawEllipse(QRectF(knob_x - 2, y - 2, 4, 4))

    painter.end()
    return QIcon(pixmap)


class V3NavigationButton(QToolButton):
    """Compact icon-and-label navigation with immediate workspace recognition."""

    def __init__(self, label: str, *, icon_name: str) -> None:
        super().__init__()
        self.setText(label)
        self._icons = {
            False: _glyph_icon(icon_name, active=False),
            True: _glyph_icon(icon_name, active=True),
        }
        self._label = label
        self.setObjectName("v3NavButton")
        self.setProperty("v3Nav", True)
        self.setProperty("active", False)
        self.setIcon(self._icons[False])
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(68, 58)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip(label)
        self.setAccessibleName(f"Open {label}")

    def set_active(self, active: bool) -> None:
        if bool(self.property("active")) == active:
            return
        self.setProperty("active", active)
        self.setIcon(self._icons[active])
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()


class V3WorkspaceHeader(QFrame):
    """Quiet contextual workbar shared by primary workspaces."""

    def __init__(self, title: str, hint: str) -> None:
        super().__init__()
        self.setObjectName("v3Workbar")
        self.setFixedHeight(68)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 10, 24, 10)
        layout.setSpacing(14)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("v3PageTitle")
        copy.addWidget(self.title_label)

        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("v3PageHint")
        copy.addWidget(self.hint_label)

        layout.addLayout(copy)
        layout.addStretch(1)

        self.action_host = QFrame()
        self.action_host.setObjectName("v3WorkbarActions")
        self.action_layout = QHBoxLayout(self.action_host)
        self.action_layout.setContentsMargins(0, 0, 0, 0)
        self.action_layout.setSpacing(8)
        layout.addWidget(self.action_host)

    def set_context(self, title: str, hint: str) -> None:
        self.title_label.setText(title)
        self.hint_label.setText(hint)


class V3Pill(QLabel):
    """Small semantic status capsule."""

    def __init__(self, text: str, *, tone: str = "neutral") -> None:
        super().__init__(text)
        self.setObjectName("v3Pill")
        self.setProperty("tone", tone)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


class V3Section(QFrame):
    """Low-chrome bounded surface used only when grouping is meaningful."""

    def __init__(self, *, object_name: str = "v3Section") -> None:
        super().__init__()
        self.setObjectName(object_name)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class V3EmptyState(QFrame):
    """Editorial empty state with no dashboard-card chrome."""

    def __init__(self, kicker: str, title: str, body: str) -> None:
        super().__init__()
        self.setObjectName("v3EmptyState")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(10)
        layout.addStretch(2)

        kicker_label = QLabel(kicker.upper())
        kicker_label.setObjectName("v3Kicker")
        kicker_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(kicker_label)

        title_label = QLabel(title)
        title_label.setObjectName("v3EmptyTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        body_label = QLabel(body)
        body_label.setObjectName("v3EmptyBody")
        body_label.setWordWrap(True)
        body_label.setMaximumWidth(560)
        body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(body_label)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(3)


class V3ControlRow(QFrame):
    """Settings row for existing real controls."""

    def __init__(self, title: str, description: str = "") -> None:
        super().__init__()
        self.setObjectName("v3ControlRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 18, 0, 18)
        layout.setSpacing(32)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("v3ControlTitle")
        copy.addWidget(title_label)

        description_label = QLabel(description)
        description_label.setObjectName("v3ControlDescription")
        description_label.setWordWrap(True)
        description_label.setVisible(bool(description))
        copy.addWidget(description_label)
        layout.addLayout(copy, 1)

        self.control_host = QWidget()
        self.control_host.setObjectName("v3ControlHost")
        self.control_layout = QHBoxLayout(self.control_host)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(8)
        self.control_host.setMinimumWidth(340)
        layout.addWidget(self.control_host)

    def add_control(self, widget: QWidget, stretch: int = 0) -> None:
        widget.setParent(self.control_host)
        self.control_layout.addWidget(widget, stretch)
