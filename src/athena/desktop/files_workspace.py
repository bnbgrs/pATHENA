"""Functional SOURCES / FILES workspace for the native pATHENA desktop shell.

Capture, representation and chunking remain canonical Core concerns.  The Qt layer
uses a short-lived helper process so source I/O and SQLite work never block the GUI.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

_SOURCE_CAPTURED_RE = re.compile(
    r"^SOURCE_CAPTURED\s+([0-9a-fA-F-]{36})$",
    re.MULTILINE,
)
_ACTIVE_READINESS = frozenset(
    {"queued", "waiting", "running", "paused", "cancel_requested"}
)


class FilesWorkspace(QWidget):
    """Capture local files and expose their real retrieval-processing readiness."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("filesWorkspace")
        self._operation = ""
        self._buffer = ""
        self._selected_source_id: str | None = None
        self._selected_readiness: str | None = None
        self._selected_processable = False

        self.import_button = QPushButton("IMPORT FILE")
        self.import_button.setObjectName("newChatButton")
        self.import_button.setToolTip(
            "Capture a local file and automatically queue retrieval processing"
        )
        self.import_button.clicked.connect(self._choose_file)

        self.refresh_button = QPushButton("REFRESH")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.process_button = QPushButton("PROCESS / RETRY")
        self.process_button.setObjectName("newChatButton")
        self.process_button.setToolTip(
            "Queue canonical source representation and chunking for the selected Source"
        )
        self.process_button.clicked.connect(self.process_selected)

        self.status = QLabel("Ready.")
        self.status.setObjectName("settingsHelp")
        self.status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        self.sources = QListWidget()
        self.sources.setObjectName("sourceList")
        self.sources.setMinimumWidth(430)
        self.sources.currentItemChanged.connect(self._selection_changed)

        self.details = QPlainTextEdit()
        self.details.setObjectName("sourceDetails")
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.details.setPlaceholderText(
            "Select a Source to inspect capture state, processing job and retrieval readiness."
        )

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._drain_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10_000)
        self._refresh_timer.timeout.connect(self._refresh_if_visible)
        self._refresh_timer.start()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("LOCAL SOURCES / FILES")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        header.addWidget(self.process_button)
        header.addWidget(self.import_button)
        layout.addLayout(header)

        intro = QLabel(
            "Import keeps the original bytes in pATHENA's immutable Raw Archive and "
            "automatically queues deterministic representation + chunking for supported "
            "TXT/Markdown, PDF, DOCX and HTML files. A Source is shown as READY only "
            "when retrieval chunks actually exist."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sources)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._sync_controls()
        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        """Load captured Sources plus their computed retrieval readiness."""
        if self._busy():
            return
        self._start("list", ["list", "--limit", "150"], "Refreshing Sources")

    def process_selected(self) -> None:
        if self._busy() or not self._selected_source_id:
            return
        self.details.clear()
        self._start(
            "process",
            ["process", self._selected_source_id],
            "Queueing Source processing",
        )

    def _choose_file(self) -> None:
        if self._busy():
            return
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Import file into pATHENA",
            str(Path.home()),
            "Supported documents (*.txt *.md *.markdown *.pdf *.docx *.html *.htm);;All files (*)",
        )
        if not selected:
            return
        self.details.clear()
        self._start(
            "import",
            ["import", selected],
            "Capturing Source and queueing retrieval processing",
        )

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        source_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        readiness = (
            None
            if current is None
            else current.data(Qt.ItemDataRole.UserRole + 1)
        )
        processable = (
            False
            if current is None
            else bool(current.data(Qt.ItemDataRole.UserRole + 2))
        )
        self._selected_source_id = str(source_id) if source_id else None
        self._selected_readiness = str(readiness) if readiness else None
        self._selected_processable = processable
        self._sync_controls()

        if self._selected_source_id and not self._busy():
            self.details.clear()
            self._start(
                "show",
                ["show", self._selected_source_id],
                "Loading Source details",
            )

    def _refresh_if_visible(self) -> None:
        if self.isVisible() and not self._busy():
            self.refresh()

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _start(self, operation: str, arguments: list[str], label: str) -> None:
        self._operation = operation
        self._buffer = ""
        self.status.setText(label + " …")
        self._sync_controls(force_disabled=True)
        self._process.start(
            sys.executable,
            ["-m", "athena.desktop.sources_cli", *arguments],
        )

    def _sync_controls(self, *, force_disabled: bool = False) -> None:
        if force_disabled or self._busy():
            self.import_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.process_button.setEnabled(False)
            return

        readiness = self._selected_readiness
        self.import_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.process_button.setEnabled(
            bool(self._selected_source_id)
            and self._selected_processable
            and readiness != "ready"
            and readiness not in _ACTIVE_READINESS
        )

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list":
            self.details.moveCursor(QTextCursor.MoveOperation.End)
            self.details.insertPlainText(chunk)

    def _process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        self._drain_output()
        operation = self._operation
        output = self._buffer
        self._operation = ""
        self._sync_controls()

        if exit_code != 0:
            self.status.setText(f"Source command failed (exit {exit_code}).")
            if operation == "list":
                self.details.setPlainText(output)
            return

        if operation == "list":
            self._render_source_list(output)
            self.status.setText(f"Sources refreshed: {self.sources.count()} shown.")
            return

        if operation == "show":
            self.status.setText("Source details loaded.")
            return

        if operation == "import":
            match = _SOURCE_CAPTURED_RE.search(output)
            if match is not None:
                self._selected_source_id = match.group(1)
            if "PROCESS_QUEUED" in output:
                self.status.setText("Source captured; retrieval processing queued.")
            elif "unsupported_format" in output:
                self.status.setText(
                    "Source captured; this format has no deterministic text processing path."
                )
            else:
                self.status.setText("Source captured.")
            QTimer.singleShot(150, self.refresh)
            return

        if operation == "process":
            if "already_ready" in output:
                self.status.setText("Source is already retrieval-ready.")
            else:
                self.status.setText("Source processing queued.")
            QTimer.singleShot(150, self.refresh)

    def _render_source_list(self, output: str) -> None:
        selected = self._selected_source_id
        self.sources.blockSignals(True)
        self.sources.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 9)
            if len(parts) != 10:
                continue
            (
                source_id,
                readiness,
                job_state,
                capture_state,
                name,
                mime_type,
                byte_length,
                processable,
                representations,
                chunks,
            ) = parts
            try:
                size_label = _format_bytes(int(byte_length))
            except ValueError:
                size_label = byte_length
            item = QListWidgetItem(
                f"{readiness.upper():<16} {size_label:>10}  {name}"
            )
            item.setToolTip(
                f"{source_id}\n"
                f"mime={mime_type}\n"
                f"capture={capture_state}\n"
                f"process_job={job_state}\n"
                f"representations={representations}\n"
                f"chunks={chunks}"
            )
            item.setData(Qt.ItemDataRole.UserRole, source_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, readiness)
            item.setData(Qt.ItemDataRole.UserRole + 2, processable == "yes")
            self.sources.addItem(item)
            if selected == source_id:
                item_to_select = item

        self.sources.blockSignals(False)
        if item_to_select is not None:
            self.sources.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.sources.count() > 0:
            self.sources.setCurrentRow(0)
        else:
            self._selected_source_id = None
            self._selected_readiness = None
            self._selected_processable = False
            self._sync_controls()
            self.details.setPlainText(
                "No Sources captured yet. Import a supported local document to preserve "
                "its original bytes and queue retrieval processing."
            )

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._operation = ""
        self._sync_controls()
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText("Unable to start the local pATHENA Source command.")
        else:
            self.status.setText(f"Source command error: {error.name}")


def _format_bytes(value: int) -> str:
    if value < 1024:
        return f"{value} B"
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KiB"
    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.1f} MiB"
    return f"{value / (1024 * 1024 * 1024):.1f} GiB"


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
