"""Predictable focus return after pATHENA dialogs close or cancel.

Command/help surfaces and native file/folder/message dialogs temporarily take keyboard
focus. This presentation-only controller remembers the previously focused usable
control and restores it after dialog close only when no newer visible focus has been
established. Command actions that intentionally move focus therefore keep ownership.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QApplication, QDialog, QWidget


class DialogFocusReturnController(QObject):
    """Restore pre-dialog focus without stealing a newer intentional focus target."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._previous: dict[QDialog, QWidget] = {}
        app = QApplication.instance()
        self.app = app if isinstance(app, QApplication) else None
        if self.app is not None:
            self.app.installEventFilter(self)
        window.setProperty("pathenaDialogFocusReturnManaged", True)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QDialog) and self._belongs_to_window(watched):
            if event.type() == QEvent.Type.Show:
                self._capture(watched)
            elif event.type() in {QEvent.Type.Hide, QEvent.Type.Close}:
                previous = self._previous.pop(watched, None)
                if previous is not None:
                    QTimer.singleShot(
                        0,
                        lambda target=previous: self._restore_if_unclaimed(target),
                    )
        return super().eventFilter(watched, event)

    def _capture(self, dialog: QDialog) -> None:
        focused = QApplication.focusWidget()
        if focused is None or self._is_descendant(focused, dialog):
            return

        previous = focused
        owning_dialog = self._tracked_dialog_for(focused)
        if owning_dialog is not None:
            inherited = self._previous.get(owning_dialog)
            if inherited is not None:
                previous = inherited

        if not self._usable(previous):
            return
        self._previous[dialog] = previous
        dialog.setProperty("pathenaFocusReturnObject", previous.objectName())
        dialog.setProperty("pathenaFocusReturnCaptured", True)
        dialog.setProperty("pathenaFocusReturnInherited", owning_dialog is not None)

    def _restore_if_unclaimed(self, previous: QWidget) -> None:
        if not self._usable(previous):
            return
        current = QApplication.focusWidget()
        if current is not None and current is not previous and self._usable(current):
            previous.setProperty("pathenaDialogFocusReturn", "preserved-newer-focus")
            return
        previous.setFocus(Qt.FocusReason.OtherFocusReason)
        previous.setProperty("pathenaDialogFocusReturn", "restored")

    def _tracked_dialog_for(self, widget: QWidget) -> QDialog | None:
        current: QWidget | None = widget
        while current is not None:
            if isinstance(current, QDialog) and current in self._previous:
                return current
            current = current.parentWidget()
        return None

    def _belongs_to_window(self, dialog: QDialog) -> bool:
        parent = dialog.parentWidget()
        while parent is not None:
            if parent is self.window:
                return True
            parent = parent.parentWidget()
        return False

    @staticmethod
    def _is_descendant(widget: QWidget, ancestor: QWidget) -> bool:
        current: QWidget | None = widget
        while current is not None:
            if current is ancestor:
                return True
            current = current.parentWidget()
        return False

    @staticmethod
    def _usable(widget: QWidget) -> bool:
        top_level = widget.window()
        return (
            top_level.isVisible()
            and widget.isVisibleTo(top_level)
            and widget.isEnabled()
            and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
        )


def install_dialog_focus_return(window: QWidget) -> DialogFocusReturnController:
    """Install focus-return arbitration for dialogs parented to the pATHENA window."""
    controller = DialogFocusReturnController(window)
    window.setProperty("pathenaDialogFocusReturnController", controller)
    return controller
