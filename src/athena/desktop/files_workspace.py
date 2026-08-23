"""Functional SOURCES / FILES workspace for the native pATHENA desktop shell.

Capture, representation and chunking remain canonical Core concerns. The Qt layer
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

from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state

_SOURCE_CAPTURED_RE = re.compile(r"^SOURCE_CAPTURED\s+([0-9a-fA-F-]{36})$", re.MULTILINE)
_ACTIVE_READINESS = frozenset({"queued", "waiting", "running", "paused", "cancel_requested"})


class FilesWorkspace(QWidget):
    """Capture local files and expose their real retrieval-processing readiness."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("filesWorkspace")
        self._operation = ""
        self._operation_source_id: str | None = None
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
        self.status.setObjectName("sourceStatus")
        self.status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        set_pathena_ui_state(self.status, "idle")

        self.sources = QListWidget()
        self.sources.setObjectName("sourceList")
        self.sources.setMinimumWidth(430)
        self.sources.currentItemChanged.connect(self._selection_changed)
        set_pathena_ui_state(self.sources, "idle")

        self.details = QPlainTextEdit()
        self.details.setObjectName("sourceDetails")
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.details.setPlaceholderText(
            "Select a Source to inspect capture state, processing job and retrieval readiness."
        )
        set_pathena_ui_state(self.details, "empty")

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

    @staticmethod
    def _source_label(source_id: str | None) -> str:
        return source_id[:8].upper() if source_id else ""

    def refresh(self) -> None:
        if self._busy():
            return
        self._start("list", ["list", "--limit", "150"], "Refreshing Sources")

    def process_selected(self) -> None:
        source_id = self._selected_source_id
        if self._busy() or not source_id:
            return
        self.details.clear()
        set_pathena_ui_state(self.details, "busy")
        self._start(
            "process",
            ["process", source_id],
            "Queueing Source processing",
            source_id=source_id,
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
        set_pathena_ui_state(self.details, "busy")
        self._start(
            "import",
            ["import", selected],
            "Capturing Source and queueing retrieval processing",
            source_id=self._selected_source_id,
        )

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        source_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        readiness = None if current is None else current.data(Qt.ItemDataRole.UserRole + 1)
        processable = (
            False
            if current is None
            else bool(current.data(Qt.ItemDataRole.UserRole + 2))
        )
        self._selected_source_id = str(source_id) if source_id else None
        self._selected_readiness = str(readiness) if readiness else None
        self._selected_processable = processable
        self._sync_controls()

        if self._busy():
            if current is not None and not self._operation_owns_details():
                selected_label = self._source_label(self._selected_source_id)
                if self._operation == "import":
                    background = "A file import is still running in the background."
                    owner = "import"
                else:
                    owner_label = self._source_label(self._operation_source_id)
                    background = (
                        f"{self._operation.upper()} for Source {owner_label} is still "
                        "running in the background."
                    )
                    owner = self._operation_source_id or ""
                self.details.setPlainText(
                    f"BACKGROUND · {background}\n"
                    f"CURRENT · Source {selected_label} remains selected; background "
                    "output will not be written into this pane.\n\n"
                    f"{current.toolTip()}"
                )
                self.details.setProperty("pathenaBackgroundOperationOwner", owner)
                set_pathena_ui_state(self.details, "idle")
            return

        self.details.setProperty("pathenaBackgroundOperationOwner", "")
        if self._selected_source_id:
            selected_source_id = self._selected_source_id
            self.details.clear()
            set_pathena_ui_state(self.details, "busy")
            self._start(
                "show",
                ["show", selected_source_id],
                "Loading Source details",
                source_id=selected_source_id,
            )

    def _refresh_if_visible(self) -> None:
        if self.isVisible() and not self._busy():
            self.refresh()

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _start(
        self,
        operation: str,
        arguments: list[str],
        label: str,
        *,
        source_id: str | None = None,
    ) -> None:
        self._operation = operation
        self._operation_source_id = source_id
        self._buffer = ""
        source_label = self._source_label(source_id)
        if source_label and operation in {"show", "process"}:
            label = f"{label} · {source_label}"
        self.status.setText(label + " …")
        set_pathena_ui_state(self.status, "busy")
        self._sync_controls(force_disabled=True)
        self._process.start(sys.executable, ["-m", "athena.desktop.sources_cli", *arguments])

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

    def _operation_owns_details(self) -> bool:
        return self._operation_source_id == self._selected_source_id

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8",
            errors="replace",
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list" and self._operation_owns_details():
            self.details.moveCursor(QTextCursor.MoveOperation.End)
            self.details.insertPlainText(chunk)

    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        operation_source_id = self._operation_source_id
        output = self._buffer
        owns_details = self._operation_owns_details()
        self._operation = ""
        self._operation_source_id = None
        self._sync_controls()
        source_label = self._source_label(operation_source_id)

        if exit_code != 0:
            subject = (
                f" for Source {source_label}"
                if source_label and operation in {"show", "process"}
                else ""
            )
            location = " in the background" if subject and not owns_details else ""
            self.status.setText(
                f"Source command{subject} failed{location} (exit {exit_code})."
            )
            set_pathena_ui_state(self.status, "error")
            if owns_details:
                set_pathena_ui_state(self.details, "error")
            if operation == "list":
                self.details.setPlainText(output)
            return

        if operation == "list":
            self._render_source_list(output)
            self.status.setText(f"Sources refreshed: {self.sources.count()} shown.")
            set_pathena_ui_state(self.status, "success")
            return

        if operation == "show":
            self.status.setText(f"Source {source_label} details loaded.")
            set_pathena_ui_state(self.status, "success")
            if owns_details:
                set_pathena_ui_state(self.details, "success")
            return

        if operation == "import":
            match = _SOURCE_CAPTURED_RE.search(output)
            captured_source_id = match.group(1) if match is not None else None
            captured_label = self._source_label(captured_source_id)
            if captured_source_id is not None and owns_details:
                self._selected_source_id = captured_source_id
            prefix = f"Source {captured_label} captured" if captured_label else "Source captured"
            if "PROCESS_QUEUED" in output:
                self.status.setText(f"{prefix}; retrieval processing queued.")
            elif "unsupported_format" in output:
                self.status.setText(
                    f"{prefix}; this format has no deterministic text processing path."
                )
            else:
                self.status.setText(f"{prefix}.")
            set_pathena_ui_state(self.status, "success")
            if owns_details:
                set_pathena_ui_state(self.details, "success")
            QTimer.singleShot(150, self.refresh)
            return

        if operation == "process":
            if "already_ready" in output:
                self.status.setText(f"Source {source_label} is already retrieval-ready.")
            else:
                self.status.setText(f"Source {source_label} processing queued.")
            set_pathena_ui_state(self.status, "success")
            if owns_details and operation_source_id == self._selected_source_id:
                set_pathena_ui_state(self.details, "success")
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
            item = QListWidgetItem(f"{readiness.upper():<16} {size_label:>10}  {name}")
            item.setToolTip(
                f"{source_id}\nmime={mime_type}\ncapture={capture_state}\n"
                f"process_job={job_state}\nrepresentations={representations}\nchunks={chunks}"
            )
            item.setData(Qt.ItemDataRole.UserRole, source_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, readiness)
            item.setData(Qt.ItemDataRole.UserRole + 2, processable == "yes")
            self.sources.addItem(item)
            if selected == source_id:
                item_to_select = item

        self.sources.blockSignals(False)
        if item_to_select is not None:
            set_pathena_ui_state(self.sources, "success")
            self.sources.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.sources.count() > 0:
            set_pathena_ui_state(self.sources, "success")
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
            set_pathena_ui_state(self.sources, "empty")
            set_pathena_ui_state(self.details, "empty")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        operation = self._operation
        source_id = self._operation_source_id
        owns_details = self._operation_owns_details()
        self._operation = ""
        self._operation_source_id = None
        self._sync_controls()
        source_label = self._source_label(source_id)
        subject = (
            f" for Source {source_label}"
            if source_label and operation in {"show", "process"}
            else ""
        )
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText(f"Unable to start the local Source command{subject}.")
        else:
            self.status.setText(f"Source command{subject} error: {error.name}")
        set_pathena_ui_state(self.status, "error")
        if owns_details:
            set_pathena_ui_state(self.details, "error")


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
