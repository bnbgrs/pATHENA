"""Reference-shell continuity for the existing PALLAS Context Inspector.

PALLAS publishes a real semantic selection when a graph snapshot arrives. The
full workspace can be opened later, after another normal route has repainted the
shared inspector. Opening PALLAS must therefore replay the already-current real
selection; no synthetic selection or semantic data is created here.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QWidget

from athena.desktop.pathena_pallas_full_view import PallasFullViewController
from athena.desktop.pathena_pallas_inspector import PallasContextInspectorController


class ReferencePallasInspectorContinuity(QObject):
    """Replay the current grounded selection when the shell-hosted view opens."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._full_view = getattr(window, "_pathena_pallas_full_view_controller", None)
        self._inspector = getattr(window, "_pathena_pallas_inspector_controller", None)
        self._grounded = window.property("pathenaPallasGroundedController")
        self._connected = (
            isinstance(self._full_view, PallasFullViewController)
            and isinstance(self._inspector, PallasContextInspectorController)
            and self._grounded is not None
        )
        if not self._connected:
            return
        self._full_view.workspace_opened.connect(self._replay_selection)
        self._full_view.workspace_closed.connect(self._restore_route_inspector)

    @Slot()
    def _replay_selection(self) -> None:
        if not self._connected:
            return
        selection = getattr(self._grounded, "_selection", None)  # noqa: SLF001
        self._inspector.set_selection(selection)

    @Slot()
    def _restore_route_inspector(self) -> None:
        if self._connected:
            self._inspector.clear_selection()

    @Slot()
    def dispose(self) -> None:
        if not self._connected:
            return
        try:
            self._full_view.workspace_opened.disconnect(self._replay_selection)
        except (RuntimeError, TypeError):
            pass
        try:
            self._full_view.workspace_closed.disconnect(self._restore_route_inspector)
        except (RuntimeError, TypeError):
            pass
        self._connected = False


def install_reference_pallas_inspector_continuity(
    window: QWidget,
) -> ReferencePallasInspectorContinuity:
    """Install the late shell-open replay without changing PALLAS data ownership."""
    existing = getattr(window, "_pathena_reference_pallas_inspector", None)
    if isinstance(existing, ReferencePallasInspectorContinuity):
        existing.dispose()
        existing.deleteLater()
    controller = ReferencePallasInspectorContinuity(window)
    window.__dict__["_pathena_reference_pallas_inspector"] = controller
    return controller
