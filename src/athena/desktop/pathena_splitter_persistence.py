"""Persistent local geometry for explicitly identified pATHENA split views."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QObject, QSettings, QTimer
from PySide6.QtWidgets import QSplitter, QWidget

_SETTINGS_ROOT = "desktop/splitters/v1"
_PERSISTENCE_KEY_PROPERTY = "pathenaSplitterPersistenceKey"
_SAVE_DEBOUNCE_MS = 180


def _default_settings() -> QSettings:
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "pATHENA",
        "pATHENA",
    )


def _normalized_state(value: object) -> QByteArray | None:
    if isinstance(value, QByteArray):
        return value if not value.isEmpty() else None
    if isinstance(value, bytes):
        state = QByteArray(value)
        return state if not state.isEmpty() else None
    return None


class SplitterPersistenceController(QObject):
    """Restore and persist only splitters with explicit stable persistence keys."""

    def __init__(
        self,
        root: QWidget,
        *,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(root)
        self.root = root
        self.settings = settings or _default_settings()
        self._splitters: dict[str, QSplitter] = {}
        self._pending: set[str] = set()
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(_SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_pending)
        self._discover_and_restore()

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._splitters))

    def _discover_and_restore(self) -> None:
        for splitter in self.root.findChildren(QSplitter):
            raw_key = splitter.property(_PERSISTENCE_KEY_PROPERTY)
            if raw_key is None:
                continue
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise RuntimeError(
                    "Persistent splitter key must be non-empty text."
                )
            key = raw_key.strip()
            if key in self._splitters:
                raise RuntimeError(
                    f"Duplicate persistent splitter key: {key}"
                )
            self._splitters[key] = splitter
            self._restore(splitter, key)
            splitter.splitterMoved.connect(
                lambda _position, _index, persistence_key=key: (
                    self._queue_save(persistence_key)
                )
            )

    def _restore(self, splitter: QSplitter, key: str) -> None:
        self.settings.beginGroup(_SETTINGS_ROOT)
        try:
            state = _normalized_state(self.settings.value(key))
        finally:
            self.settings.endGroup()
        if state is not None:
            splitter.restoreState(state)

    def _queue_save(self, key: str) -> None:
        if key not in self._splitters:
            return
        self._pending.add(key)
        self._save_timer.start()

    def _flush_pending(self) -> None:
        if not self._pending:
            return
        pending = tuple(sorted(self._pending))
        self._pending.clear()
        self.settings.beginGroup(_SETTINGS_ROOT)
        try:
            for key in pending:
                splitter = self._splitters.get(key)
                if splitter is not None:
                    self.settings.setValue(key, splitter.saveState())
        finally:
            self.settings.endGroup()
        self.settings.sync()

    def dispose(self) -> None:
        """Flush pending user geometry before application teardown."""
        if self._save_timer.isActive():
            self._save_timer.stop()
        self._flush_pending()


def install_splitter_persistence(
    root: QWidget,
    *,
    settings: QSettings | None = None,
) -> SplitterPersistenceController:
    """Install versioned local persistence for all explicitly marked splitters."""
    controller = SplitterPersistenceController(
        root,
        settings=settings,
    )
    root.setProperty("pathenaSplitterPersistenceEnabled", True)
    root.setProperty("pathenaSplitterPersistenceCount", len(controller.keys))
    return controller
