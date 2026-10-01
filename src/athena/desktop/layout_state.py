"""Persist non-semantic desktop layout state across pATHENA sessions."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QByteArray, QEvent, QObject, QSettings, QTimer, Slot
from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget

_LAYOUT_GROUP = "desktop/layout/v1"
_LAYOUT_VERSION = 1
_SAVE_DEBOUNCE_MS = 700
_MAX_PERSISTED_SPLITTERS = 64


@dataclass(frozen=True, slots=True)
class _SplitterEntry:
    identity: str
    splitter: QSplitter


class DesktopLayoutStateController(QObject):
    """Persist window geometry and real Qt splitter state without domain data."""

    def __init__(
        self,
        window: QMainWindow,
        *,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.settings = settings or QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "pATHENA",
            "desktop",
        )
        self._restored = False
        self._restoring = False

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(_SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self.save)

        self.window.installEventFilter(self)
        for entry in self._splitter_entries():
            entry.splitter.splitterMoved.connect(self._schedule_save)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.window and event.type() in {
            QEvent.Type.Move,
            QEvent.Type.Resize,
            QEvent.Type.WindowStateChange,
        }:
            self._schedule_save()
        return False

    @Slot()
    def restore(self) -> None:
        """Restore only a compatible layout snapshot and ignore stale/corrupt values."""

        if self._restored:
            return

        self._restoring = True
        try:
            self.settings.beginGroup(_LAYOUT_GROUP)
            try:
                version = _settings_int(self.settings, "version")
                if version != _LAYOUT_VERSION:
                    return

                geometry = _byte_array(self.settings.value("window_geometry"))
                if geometry is not None:
                    self.window.restoreGeometry(geometry)

                stored = _stored_splitter_states(self.settings)
                current = {
                    entry.identity: entry.splitter
                    for entry in self._splitter_entries()
                }
                for identity, state in stored.items():
                    splitter = current.get(identity)
                    if splitter is not None:
                        splitter.restoreState(state)
            finally:
                self.settings.endGroup()
        finally:
            self._restoring = False
            self._restored = True

    @Slot()
    def save(self) -> None:
        """Atomically replace the versioned local layout snapshot in QSettings."""

        if self._restoring:
            return

        entries = self._splitter_entries()[:_MAX_PERSISTED_SPLITTERS]
        self.settings.beginGroup(_LAYOUT_GROUP)
        try:
            self.settings.remove("")
            self.settings.setValue("version", _LAYOUT_VERSION)
            self.settings.setValue("window_geometry", self.window.saveGeometry())
            self.settings.setValue("splitters/count", len(entries))
            for index, entry in enumerate(entries):
                prefix = f"splitters/{index}"
                self.settings.setValue(f"{prefix}/identity", entry.identity)
                self.settings.setValue(f"{prefix}/state", entry.splitter.saveState())
        finally:
            self.settings.endGroup()
        self.settings.sync()

    def _schedule_save(self, *_args: object) -> None:
        if not self._restored or self._restoring:
            return
        self._save_timer.start()

    def _splitter_entries(self) -> list[_SplitterEntry]:
        counts: dict[tuple[str, str], int] = {}
        entries: list[_SplitterEntry] = []

        for splitter in self.window.findChildren(QSplitter):
            workspace = _workspace_identity(splitter, self.window)
            splitter_name = splitter.objectName().strip() or "splitter"
            base = (workspace, splitter_name)
            occurrence = counts.get(base, 0)
            counts[base] = occurrence + 1
            identity = f"{workspace}:{splitter_name}:{occurrence}"
            entries.append(_SplitterEntry(identity=identity, splitter=splitter))

        return entries


def _workspace_identity(splitter: QSplitter, window: QMainWindow) -> str:
    parent: QWidget | None = splitter.parentWidget()
    while parent is not None and parent is not window:
        name = parent.objectName().strip()
        if name and name.casefold().endswith("workspace"):
            return name
        parent = parent.parentWidget()

    window_name = window.objectName().strip()
    return window_name or "mainWindow"


def _stored_splitter_states(settings: QSettings) -> dict[str, QByteArray]:
    count = _settings_int(settings, "splitters/count")
    if count is None or count < 0:
        return {}

    states: dict[str, QByteArray] = {}
    for index in range(min(count, _MAX_PERSISTED_SPLITTERS)):
        prefix = f"splitters/{index}"
        identity = settings.value(f"{prefix}/identity")
        state = _byte_array(settings.value(f"{prefix}/state"))
        if isinstance(identity, str) and identity.strip() and state is not None:
            states[identity] = state
    return states


def _settings_int(settings: QSettings, key: str) -> int | None:
    value = settings.value(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _byte_array(value: object) -> QByteArray | None:
    if isinstance(value, QByteArray):
        return value
    if isinstance(value, (bytes, bytearray)):
        return QByteArray(bytes(value))
    return None


def install_desktop_layout_state(
    window: QMainWindow,
    *,
    settings: QSettings | None = None,
) -> DesktopLayoutStateController:
    """Attach persistent, local-only layout state to the finished desktop shell."""

    return DesktopLayoutStateController(window, settings=settings)
