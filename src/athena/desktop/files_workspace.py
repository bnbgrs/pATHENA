"""Functional FILES workspace for the native pATHENA desktop shell.

The desktop deliberately reuses the canonical ``athena source`` CLI boundary here.
This keeps source capture, hashing, retention and persistence on the same production
path as non-GUI use instead of introducing a second file-ingestion implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FilesWorkspace(QWidget):
    """Capture local files and inspect canonical Source records without blocking Qt."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("filesWorkspace")
        self._operation = ""

        self.import_button = QPushButton("IMPORT FILE")
        self.import_button.setObjectName("newChatButton")
        self.import_button.setToolTip("Capture a local file into pATHENA Sources")
        self.import_button.clicked.connect(self._choose_file)

        self.refresh_button = QPushButton("REFRESH SOURCES")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.status = QLabel("Ready.")
        self.status.setObjectName("settingsHelp")
        self.status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        self.output = QPlainTextEdit()
        self.output.setObjectName("filesSourceOutput")
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Captured Sources will appear here.")
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._drain_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("LOCAL SOURCES / FILES")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        header.addWidget(self.import_button)
        layout.addLayout(header)

        intro = QLabel(
            "Capture files into pATHENA's canonical Source store. Import uses the same "
            "content-addressed source pipeline as the CLI; no duplicate desktop storage "
            "path is created."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        layout.addWidget(self.status)
        layout.addWidget(self.output, 1)

        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        """List persisted Sources through the canonical local CLI boundary."""
        if self._process.state() != QProcess.ProcessState.NotRunning:
            return
        self.output.clear()
        self._start("Refreshing Sources", ["source", "list", "--limit", "100"])

    def _choose_file(self) -> None:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            return
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Import file into pATHENA",
            str(Path.home()),
            "All files (*)",
        )
        if not selected:
            return
        self.output.clear()
        self._start("Importing file", ["source", "import", selected])

    def _start(self, operation: str, arguments: list[str]) -> None:
        self._operation = operation
        self.status.setText(operation + " …")
        self.import_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self._process.start(sys.executable, ["-m", "athena", *arguments])

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if chunk:
            self.output.moveCursor(QTextCursor.MoveOperation.End)
            self.output.insertPlainText(chunk)

    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        self._operation = ""
        self.import_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        if exit_code == 0:
            self.status.setText(operation + " complete.")
            if operation == "Importing file":
                QTimer.singleShot(150, self.refresh)
            return
        self.status.setText(f"{operation} failed (exit {exit_code}).")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self.import_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText("Unable to start the local pATHENA source command.")
        else:
            self.status.setText(f"Source command error: {error.name}")


def install_files_workspace(window: object) -> FilesWorkspace:
    """Replace the FILES shell placeholder without widening window.py."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 4:
        raise RuntimeError("pATHENA desktop FILES page is unavailable")

    placeholder = pages.widget(4)
    workspace = FilesWorkspace()
    pages.removeWidget(placeholder)
    pages.insertWidget(4, workspace)
    placeholder.deleteLater()
    return workspace
