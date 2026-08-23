"""Reactive local visual-state surface used by the pATHENA desktop shell."""

from __future__ import annotations

import hashlib
import random

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPlainTextEdit, QWidget

from athena.desktop.theme import ORANGE

_COLS = 25
_ROWS = 42
_TICK_MS = 220
_SEMANTIC_SAMPLE_TICKS = 5
_MAX_SEMANTIC_ITEMS = 20
_MAX_SEMANTIC_CHARS = 2_400
_GLYPHS = ("·", ":", "+", "o", "O", "░", "▒", "▓", "█")


def _context_seed(context: str) -> int:
    digest = hashlib.blake2b(context.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def _seed_grid(context: str) -> list[list[int]]:
    """Create a deterministic but semantically varied initial cellular field."""
    normalized = context.casefold().strip() or "idle"
    rng = random.Random(_context_seed(normalized))

    density = 0.19
    if "research" in normalized or "source" in normalized or "file" in normalized:
        density = 0.24
    elif "knowledge" in normalized:
        density = 0.28
    elif "job" in normalized or "system" in normalized:
        density = 0.22

    grid = [[0 for _ in range(_COLS)] for _ in range(_ROWS)]
    for row in range(_ROWS):
        for col in range(_COLS):
            if rng.random() < density:
                grid[row][col] = rng.randint(1, 4)

    # Give every context a stable semantic nucleus instead of pure visual noise.
    center_row = _ROWS // 2
    center_col = _COLS // 2
    for delta_row, delta_col in (
        (0, 0),
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, 1),
    ):
        grid[(center_row + delta_row) % _ROWS][
            (center_col + delta_col) % _COLS
        ] = 5
    return grid


def _step_grid(grid: list[list[int]]) -> list[list[int]]:
    """Advance one bounded Conway-like generation while retaining cell age."""
    next_grid = [[0 for _ in range(_COLS)] for _ in range(_ROWS)]
    for row in range(_ROWS):
        for col in range(_COLS):
            neighbors = 0
            for delta_row in (-1, 0, 1):
                for delta_col in (-1, 0, 1):
                    if delta_row == 0 and delta_col == 0:
                        continue
                    neighbor_row = row + delta_row
                    neighbor_col = col + delta_col
                    if not (0 <= neighbor_row < _ROWS and 0 <= neighbor_col < _COLS):
                        continue
                    if grid[neighbor_row][neighbor_col] > 0:
                        neighbors += 1

            age = grid[row][col]
            if age > 0 and neighbors in (2, 3):
                next_grid[row][col] = min(age + 1, len(_GLYPHS))
            elif age == 0 and neighbors == 3:
                next_grid[row][col] = 1
    return next_grid


def _grid_text(grid: list[list[int]]) -> str:
    return "\n".join(
        "".join(_GLYPHS[min(age, len(_GLYPHS)) - 1] if age else " " for age in row)
        for row in grid
    )


def ascii_scene(context: str) -> tuple[str, ...]:
    """Return the deterministic initial scene for a semantic context label."""
    return tuple(_grid_text(_seed_grid(context)).splitlines())


def _normalized_semantic_text(value: str) -> str:
    return " ".join(value.casefold().split())


class AsciiPanel(QPlainTextEdit):
    """Drive the live PALLAS field and remain usable as a compact text surface.

    The current desktop shell still owns a legacy ``PallasVisualPlaceholder`` in
    ``window.py``. This controller binds to that widget at runtime and replaces
    its paint event. The cellular field is local-only and samples visible desktop
    text so PALLAS reacts to the active conversation, knowledge and research
    material without requiring a model call or network access.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("asciiPanel")
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFixedHeight(134)

        self._context = "idle"
        self._semantic_signature = ""
        self._semantic_sample = ""
        self._generation = 0
        self._grid = _seed_grid(self._context)
        self._pallas_target: QWidget | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(_TICK_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self._refresh_text_surface()

    def set_context(self, context: str) -> None:
        normalized = context.casefold().strip() or "idle"
        if normalized != self._context:
            self._context = normalized
            self._semantic_signature = ""
            self._semantic_sample = ""
            self._generation = 0
            self._grid = _seed_grid(normalized)
        self._refresh_text_surface()
        self._bind_pallas_target()
        self._sync_semantic_context(force=True)
        if self._pallas_target is not None:
            self._pallas_target.update()

    def _tick(self) -> None:
        self._bind_pallas_target()
        if self._generation % _SEMANTIC_SAMPLE_TICKS == 0:
            self._sync_semantic_context()
        next_grid = _step_grid(self._grid)
        if not any(any(row) for row in next_grid):
            seed_context = self._semantic_seed_context()
            next_grid = _seed_grid(f"{seed_context}:{self._generation // 24}")
        self._grid = next_grid
        self._generation += 1
        self._refresh_text_surface()
        if self._pallas_target is not None:
            self._pallas_target.update()

    def _semantic_seed_context(self) -> str:
        if not self._semantic_sample:
            return self._context
        return f"{self._context}|{self._semantic_sample}"

    def _sync_semantic_context(self, *, force: bool = False) -> None:
        sample = self._semantic_snapshot()
        signature = hashlib.blake2b(sample.encode("utf-8"), digest_size=8).hexdigest()
        if not force and signature == self._semantic_signature:
            return

        previous_signature = self._semantic_signature
        self._semantic_signature = signature
        self._semantic_sample = sample
        if force and not previous_signature:
            return

        # Visible content changed: evolve from a deterministic representation of
        # the current workspace + content instead of restarting from random noise.
        self._generation = 0
        self._grid = _seed_grid(self._semantic_seed_context())

    def _semantic_snapshot(self) -> str:
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return self._context

        root = app.activeWindow()
        if root is None:
            root = self.window()
        if not isinstance(root, QWidget):
            return self._context

        items: list[str] = []
        total_chars = 0

        def append(value: str) -> None:
            nonlocal total_chars
            normalized = _normalized_semantic_text(value)
            if not normalized or normalized in items:
                return
            remaining = _MAX_SEMANTIC_CHARS - total_chars
            if remaining <= 0:
                return
            clipped = normalized[:remaining]
            items.append(clipped)
            total_chars += len(clipped)

        # Prompt text is intentionally included so the field begins responding
        # while the user is composing, before a message is sent.
        for line_edit in root.findChildren(QLineEdit):
            if len(items) >= _MAX_SEMANTIC_ITEMS:
                break
            if line_edit is self or not line_edit.isVisible():
                continue
            append(line_edit.text())

        # Chat messages, selected knowledge/research metadata and inspector text
        # are labels in the current desktop shell. Hidden pages are excluded.
        for label in root.findChildren(QLabel):
            if len(items) >= _MAX_SEMANTIC_ITEMS or total_chars >= _MAX_SEMANTIC_CHARS:
                break
            if not label.isVisible():
                continue
            append(label.text())

        if not items:
            return self._context
        return " | ".join(items)

    def _bind_pallas_target(self) -> None:
        if self._pallas_target is not None:
            return
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return
        for widget in app.allWidgets():
            if widget.objectName() != "pallasVisualPlaceholder":
                continue
            self._pallas_target = widget
            widget.installEventFilter(self)
            widget.setToolTip(
                "PALLAS — live local semantic cellular field; reacts to visible workspace content"
            )
            widget.destroyed.connect(self._pallas_destroyed)
            widget.update()
            return

    def _pallas_destroyed(self, _object: QObject | None = None) -> None:
        self._pallas_target = None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._pallas_target and event.type() == QEvent.Type.Paint:
            if isinstance(watched, QWidget):
                self._paint_pallas(watched)
                return True
        return super().eventFilter(watched, event)

    def _paint_pallas(self, target: QWidget) -> None:
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        width = target.width()
        height = target.height()

        painter.fillRect(target.rect(), QColor("#070707"))
        painter.setPen(QPen(QColor("#242424"), 1))
        painter.drawRect(0, 0, width - 1, height - 1)

        font = QFont("Cascadia Mono")
        font.setPixelSize(9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        painter.setFont(font)

        painter.setPen(QColor("#F2F1ED"))
        painter.drawText(13, 21, "PALLAS")
        painter.setPen(QColor("#6F6F6B"))
        context_label = self._context.upper()[:12]
        metrics = painter.fontMetrics()
        painter.drawText(width - 13 - metrics.horizontalAdvance(context_label), 21, context_label)

        left = 14
        top = 37
        usable_width = max(1, width - 28)
        usable_height = max(1, height - top - 30)
        cell_width = usable_width / _COLS
        cell_height = usable_height / _ROWS

        for row_index, row in enumerate(self._grid):
            for col_index, age in enumerate(row):
                if age <= 0:
                    continue
                glyph = _GLYPHS[min(age, len(_GLYPHS)) - 1]
                if age >= 7:
                    painter.setPen(QColor(ORANGE))
                elif age >= 4:
                    painter.setPen(QColor("#B7B6B0"))
                else:
                    painter.setPen(QColor("#62625E"))
                x = int(left + col_index * cell_width)
                y = int(top + (row_index + 1) * cell_height)
                painter.drawText(x, y, glyph)

        painter.setPen(QColor("#50504C"))
        semantic_state = "SEMANTIC" if self._semantic_sample != self._context else "LOCAL"
        generation = f"GEN {self._generation:04d} / {semantic_state}"
        painter.drawText(13, height - 11, generation)
        painter.end()

    def _refresh_text_surface(self) -> None:
        self.setPlainText(_grid_text(self._grid))
        self._accent_center()

    def _accent_center(self) -> None:
        document = self.document()
        cursor = QTextCursor(document)
        text = document.toPlainText()
        center = len(text) // 2
        while center < len(text) and text[center].isspace():
            center += 1
        if center >= len(text):
            return
        cursor.setPosition(center)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(ORANGE))
        cursor.mergeCharFormat(char_format)
