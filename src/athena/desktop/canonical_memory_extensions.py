"""Progressive canonical-memory controls for the pATHENA Knowledge workspace.

The base KnowledgeWorkspace owns durable list/detail flows.  This controller adds
merge-candidate decisions, claim-to-claim relation navigation, filtering and copy
utilities without duplicating canonical stores or semantic write rules.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QProcess, Qt, QTimer, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from athena.desktop.knowledge_workspace import KnowledgeWorkspace


class CanonicalMemoryExtension(QObject):
    """Add explicit merge review and relation traversal to one Knowledge workspace."""

    def __init__(self, workspace: KnowledgeWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._merge_operation = ""
        self._merge_buffer = ""
        self._relation_buffer = ""

        self.merge_process = QProcess(self)
        self.merge_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.merge_process.readyReadStandardOutput.connect(self._drain_merge_output)
        self.merge_process.finished.connect(self._merge_finished)
        self.merge_process.errorOccurred.connect(self._merge_error)

        self.relation_process = QProcess(self)
        self.relation_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.relation_process.readyReadStandardOutput.connect(self._drain_relation_output)
        self.relation_process.finished.connect(self._relation_finished)
        self.relation_process.errorOccurred.connect(self._relation_error)

        self._install_decision_mode()
        self._install_relation_panel()
        self._install_browser_utilities()
        self._rewire_refresh()

        workspace._knowledge_process.finished.connect(self._schedule_sync)
        workspace.browser_tabs.currentChanged.connect(self._tab_changed)
        workspace.claim_list.currentItemChanged.connect(self._claim_selection_seen)
        QTimer.singleShot(0, self._sync_counts)

    def _install_decision_mode(self) -> None:
        self.decision_mode = QComboBox()
        self.decision_mode.setObjectName("semanticDecisionMode")
        self.decision_mode.addItem("Contradictions", "contradiction")
        self.decision_mode.addItem("Merge candidates", "merge_candidate")
        self.decision_mode.setToolTip(
            "Switch between contradiction decisions and canonical near-duplicate merge reviews"
        )
        left = self.workspace.review_list.parentWidget()
        left_layout = None if left is None else left.layout()
        if isinstance(left_layout, QVBoxLayout):
            left_layout.insertWidget(1, self.decision_mode)

        try:
            self.workspace.review_list.currentItemChanged.disconnect(
                self.workspace._review_selection_changed
            )
        except (RuntimeError, TypeError):
            pass
        self.workspace.review_list.currentItemChanged.connect(
            self._review_selection_changed
        )

        try:
            self.workspace.review_accept_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        try:
            self.workspace.review_reject_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        self.workspace.review_accept_button.clicked.connect(self._primary_decision)
        self.workspace.review_reject_button.clicked.connect(self._secondary_decision)
        self.decision_mode.currentIndexChanged.connect(self._decision_mode_changed)
        self._sync_decision_button_copy()

    def _install_relation_panel(self) -> None:
        self.relation_status = QLabel("Relations load with the selected Claim.")
        self.relation_status.setObjectName("settingsHelp")
        self.relation_list = QListWidget()
        self.relation_list.setObjectName("claimRelationList")
        self.relation_list.setMaximumHeight(170)
        self.relation_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.open_related_button = QPushButton("OPEN RELATED CLAIM")
        self.open_related_button.setObjectName("newChatButton")
        self.open_related_button.setEnabled(False)
        self.open_related_button.clicked.connect(self._open_related_claim)
        self.relation_list.currentItemChanged.connect(self._relation_selection_changed)

        parent = self.workspace.claim_details.parentWidget()
        layout = None if parent is None else parent.layout()
        if isinstance(layout, QVBoxLayout):
            header = QHBoxLayout()
            heading = QLabel("RELATIONS / EVIDENCE LINKS")
            heading.setProperty("role", "section")
            header.addWidget(heading)
            header.addStretch(1)
            header.addWidget(self.open_related_button)
            layout.addLayout(header)
            layout.addWidget(self.relation_status)
            layout.addWidget(self.relation_list)

    def _install_browser_utilities(self) -> None:
        self.clear_filter_button = QPushButton("CLEAR")
        self.clear_filter_button.setObjectName("newChatButton")
        self.clear_filter_button.setToolTip("Clear canonical-memory filter")
        self.clear_filter_button.clicked.connect(self.workspace.search_input.clear)

        root = self.workspace.layout()
        if isinstance(root, QVBoxLayout):
            index = root.indexOf(self.workspace.search_input)
            if index >= 0:
                root.removeWidget(self.workspace.search_input)
                row = QHBoxLayout()
                row.addWidget(self.workspace.search_input, 1)
                row.addWidget(self.clear_filter_button)
                root.insertLayout(index, row)

            self.counts = QLabel("Knowledge 0 · Claims 0 · Decisions 0")
            self.counts.setObjectName("settingsHelp")
            status_index = root.indexOf(self.workspace.browser_status)
            root.insertWidget(status_index + 1, self.counts)

        try:
            self.workspace.search_input.textChanged.disconnect(self.workspace._apply_filter)
        except (RuntimeError, TypeError):
            pass
        self.workspace.search_input.textChanged.connect(self._apply_filter)

        self.find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self.workspace)
        self.find_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.find_shortcut.activated.connect(self._focus_filter)

        self.knowledge_copy_id = QPushButton("COPY ID")
        self.knowledge_copy_details = QPushButton("COPY DETAILS")
        self.claim_copy_id = QPushButton("COPY ID")
        self.claim_copy_details = QPushButton("COPY DETAILS")
        for button in (
            self.knowledge_copy_id,
            self.knowledge_copy_details,
            self.claim_copy_id,
            self.claim_copy_details,
        ):
            button.setObjectName("newChatButton")

        self.knowledge_copy_id.clicked.connect(
            lambda: self._copy_text(self.workspace._selected_knowledge_id)
        )
        self.knowledge_copy_details.clicked.connect(
            lambda: self._copy_editor(self.workspace.knowledge_details)
        )
        self.claim_copy_id.clicked.connect(
            lambda: self._copy_text(self.workspace._selected_claim_id)
        )
        self.claim_copy_details.clicked.connect(
            lambda: self._copy_editor(self.workspace.claim_details)
        )
        self._append_copy_row(
            self.workspace.knowledge_details,
            self.knowledge_copy_id,
            self.knowledge_copy_details,
        )
        self._append_copy_row(
            self.workspace.claim_details,
            self.claim_copy_id,
            self.claim_copy_details,
        )

    def _append_copy_row(
        self,
        editor: QPlainTextEdit,
        copy_id: QPushButton,
        copy_details: QPushButton,
    ) -> None:
        parent = editor.parentWidget()
        layout = None if parent is None else parent.layout()
        if not isinstance(layout, QVBoxLayout):
            return
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(copy_id)
        row.addWidget(copy_details)
        editor_index = layout.indexOf(editor)
        layout.insertLayout(editor_index + 1, row)

    def _rewire_refresh(self) -> None:
        try:
            self.workspace.refresh_knowledge_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        self.workspace.refresh_knowledge_button.clicked.connect(self.refresh_current_view)
        try:
            self.workspace._knowledge_refresh_timer.timeout.disconnect(
                self.workspace._refresh_knowledge_if_visible
            )
        except (RuntimeError, TypeError):
            pass
        self.workspace._knowledge_refresh_timer.timeout.connect(self._periodic_refresh)

    @Slot()
    def refresh_current_view(self) -> None:
        if (
            self.workspace.browser_tabs.currentIndex() == 2
            and self.decision_mode.currentData() == "merge_candidate"
        ):
            self._refresh_merge_candidates()
            return
        self.workspace.refresh_knowledge()

    @Slot()
    def _periodic_refresh(self) -> None:
        if self.workspace.isVisible():
            self.refresh_current_view()

    @Slot(int)
    def _tab_changed(self, index: int) -> None:
        if index == 2 and self.decision_mode.currentData() == "merge_candidate":
            QTimer.singleShot(80, self._refresh_merge_candidates)
        self._schedule_sync()

    @Slot(int)
    def _decision_mode_changed(self, _index: int) -> None:
        self.workspace._selected_review_id = None
        self.workspace.review_list.clear()
        self.workspace.review_details.clear()
        self._sync_decision_button_copy()
        if self.workspace.browser_tabs.currentIndex() == 2:
            QTimer.singleShot(0, self.refresh_current_view)

    def _sync_decision_button_copy(self) -> None:
        merge_mode = self.decision_mode.currentData() == "merge_candidate"
        self.workspace.review_accept_button.setText(
            "MERGE" if merge_mode else "ACCEPT CONTRADICTION"
        )
        self.workspace.review_reject_button.setText(
            "KEEP SEPARATE" if merge_mode else "REJECT"
        )
        self.workspace.review_accept_button.setToolTip(
            "Reuse the reviewed canonical entity for this proposal"
            if merge_mode
            else "Create reciprocal contradiction evidence for both Claims"
        )
        self.workspace.review_reject_button.setToolTip(
            "Keep the proposed semantic entity separate from the near-duplicate"
            if merge_mode
            else "Reject the contradiction without creating semantic evidence"
        )
        enabled = bool(self.workspace._selected_review_id)
        self.workspace.review_accept_button.setEnabled(enabled)
        self.workspace.review_reject_button.setEnabled(enabled)

    def _review_selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        if self.decision_mode.currentData() != "merge_candidate":
            self.workspace._review_selection_changed(current, previous)
            self._sync_decision_button_copy()
            return

        review_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self.workspace._selected_review_id = str(review_id) if review_id else None
        self._sync_decision_button_copy()
        if self.workspace._selected_review_id:
            self._start_merge(
                "merge-show",
                ["merge-show", self.workspace._selected_review_id],
                clear_details=True,
            )

    @Slot()
    def _primary_decision(self) -> None:
        review_id = self.workspace._selected_review_id
        if not review_id:
            return
        if self.decision_mode.currentData() == "merge_candidate":
            self._start_merge("merge", ["merge", review_id], clear_details=True)
            return
        self.workspace.accept_selected_review()

    @Slot()
    def _secondary_decision(self) -> None:
        review_id = self.workspace._selected_review_id
        if not review_id:
            return
        if self.decision_mode.currentData() == "merge_candidate":
            self._start_merge(
                "keep-separate",
                ["keep-separate", review_id],
                clear_details=True,
            )
            return
        self.workspace.reject_selected_review()

    def _refresh_merge_candidates(self) -> None:
        self._start_merge("merge-list", ["merge-list", "--limit", "200"])

    def _merge_busy(self) -> bool:
        return self.merge_process.state() != QProcess.ProcessState.NotRunning

    def _start_merge(
        self,
        operation: str,
        arguments: list[str],
        *,
        clear_details: bool = False,
    ) -> None:
        if self._merge_busy():
            return
        self._merge_operation = operation
        self._merge_buffer = ""
        if clear_details:
            self.workspace.review_details.clear()
        self.workspace.browser_status.setText(
            {
                "merge-list": "Refreshing canonical merge candidates …",
                "merge-show": "Loading canonical merge target …",
                "merge": "Saving explicit MERGE decision …",
                "keep-separate": "Saving explicit KEEP SEPARATE decision …",
            }.get(operation, "Updating canonical-memory decision …")
        )
        self.merge_process.start(
            sys.executable,
            ["-m", "athena.desktop.canonical_memory_cli", *arguments],
        )

    @Slot()
    def _drain_merge_output(self) -> None:
        chunk = bytes(self.merge_process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._merge_buffer += chunk
        if self._merge_operation in {"merge-show", "merge", "keep-separate"}:
            self.workspace.review_details.moveCursor(
                self.workspace.review_details.textCursor().MoveOperation.End
            )
            self.workspace.review_details.insertPlainText(chunk)

    @Slot(int, QProcess.ExitStatus)
    def _merge_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._drain_merge_output()
        operation = self._merge_operation
        output = self._merge_buffer
        self._merge_operation = ""
        if exit_code != 0:
            self.workspace.browser_status.setText(
                f"Canonical merge command failed (exit {exit_code})."
            )
            if output and not self.workspace.review_details.toPlainText():
                self.workspace.review_details.setPlainText(output)
            return

        if operation == "merge-list":
            self._render_merge_list(output)
            self.workspace.browser_status.setText(
                f"Pending merge candidates: {self.workspace.review_list.count()} shown."
            )
        elif operation == "merge-show":
            self.workspace.browser_status.setText("Canonical merge proposal and target loaded.")
        elif operation in {"merge", "keep-separate"}:
            decision = "MERGE" if operation == "merge" else "KEEP SEPARATE"
            self.workspace.browser_status.setText(f"{decision} decision persisted.")
            self.workspace._selected_review_id = None
            QTimer.singleShot(120, self._refresh_merge_candidates)
        self._schedule_sync()

    def _render_merge_list(self, output: str) -> None:
        selected = self.workspace._selected_review_id
        self.workspace.review_list.blockSignals(True)
        self.workspace.review_list.clear()
        selected_item: QListWidgetItem | None = None
        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 7)
            if len(parts) != 8:
                continue
            (
                review_id,
                proposal_type,
                proposal_index,
                similarity,
                target_id,
                kind,
                status,
                text,
            ) = parts
            try:
                percent = float(similarity) * 100
            except ValueError:
                percent = 0.0
            item = QListWidgetItem(
                f"{percent:5.1f}%  {proposal_type.upper():<10} {kind.upper():<14}  {text}"
            )
            item.setToolTip(
                f"{review_id}\nproposal={proposal_index}\ntarget={target_id}\nstatus={status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, review_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, "merge_candidate")
            self.workspace.review_list.addItem(item)
            if review_id == selected:
                selected_item = item
        self.workspace.review_list.blockSignals(False)
        if selected_item is not None:
            self.workspace.review_list.setCurrentItem(selected_item)
        elif self.workspace.review_list.count() > 0:
            self.workspace.review_list.setCurrentRow(0)
        else:
            self.workspace._selected_review_id = None
            self.workspace.review_details.setPlainText(
                "No pending canonical merge candidates. Near-duplicate proposals require "
                "an explicit MERGE or KEEP SEPARATE decision before acceptance."
            )
            self._sync_decision_button_copy()
        self._apply_filter(self.workspace.search_input.text())

    @Slot(QProcess.ProcessError)
    def _merge_error(self, error: QProcess.ProcessError) -> None:
        self._merge_operation = ""
        self.workspace.browser_status.setText(
            "Unable to start canonical-memory decision command."
            if error == QProcess.ProcessError.FailedToStart
            else f"Canonical-memory decision error: {error.name}"
        )

    def _claim_selection_seen(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self.relation_list.clear()
            self.relation_status.setText("No Claim selected.")
            self.open_related_button.setEnabled(False)
            return
        QTimer.singleShot(80, self._load_selected_relations)

    def _load_selected_relations(self) -> None:
        claim_id = self.workspace._selected_claim_id
        if not claim_id or self.relation_process.state() != QProcess.ProcessState.NotRunning:
            return
        self._relation_buffer = ""
        self.relation_status.setText("Loading evidence relations …")
        self.relation_process.start(
            sys.executable,
            [
                "-m",
                "athena.desktop.canonical_memory_cli",
                "claim-relations",
                claim_id,
            ],
        )

    @Slot()
    def _drain_relation_output(self) -> None:
        chunk = bytes(self.relation_process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if chunk:
            self._relation_buffer += chunk

    @Slot(int, QProcess.ExitStatus)
    def _relation_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._drain_relation_output()
        if exit_code != 0:
            self.relation_status.setText(f"Claim relation command failed (exit {exit_code}).")
            return
        self._render_relations(self._relation_buffer)
        self._schedule_sync()

    def _render_relations(self, output: str) -> None:
        self.relation_list.clear()
        declared_count = 0
        for raw_line in output.splitlines():
            if raw_line.startswith("RELATION_COUNT "):
                try:
                    declared_count = int(raw_line.split(" ", 1)[1])
                except ValueError:
                    declared_count = 0
                continue
            if not raw_line.startswith("RELATION\t"):
                continue
            parts = raw_line.split("\t", 7)
            if len(parts) != 8:
                continue
            _, role, target_id, revision_id, target_type, kind, status, text = parts
            item = QListWidgetItem(
                f"{role.upper():<14} {target_type.upper():<8} {kind.upper():<12}  {text}"
            )
            item.setToolTip(
                f"target={target_id}\nrevision={revision_id}\ntype={target_type}\nstatus={status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, target_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, target_type)
            self.relation_list.addItem(item)
        count = self.relation_list.count()
        self.relation_status.setText(
            f"{count} evidence relation{'s' if count != 1 else ''}"
            + ("" if declared_count == count else f" · reported {declared_count}")
        )
        if count > 0:
            self.relation_list.setCurrentRow(0)
        else:
            self.open_related_button.setEnabled(False)

    def _relation_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        target_type = None if current is None else current.data(Qt.ItemDataRole.UserRole + 1)
        self.open_related_button.setEnabled(target_type == "claim")

    @Slot()
    def _open_related_claim(self) -> None:
        item = self.relation_list.currentItem()
        if item is None or item.data(Qt.ItemDataRole.UserRole + 1) != "claim":
            return
        target_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(target_id, str) or not target_id:
            return

        for index in range(self.workspace.claim_list.count()):
            candidate = self.workspace.claim_list.item(index)
            if candidate.data(Qt.ItemDataRole.UserRole) == target_id:
                self.workspace.claim_list.setCurrentItem(candidate)
                return

        if self.workspace._knowledge_busy():
            return
        self.workspace._selected_claim_id = target_id
        self.workspace.claim_details.clear()
        self.workspace._start_knowledge(
            "claim-show",
            ["claim-show", target_id],
            "Loading related canonical Claim",
        )
        QTimer.singleShot(120, self._load_selected_relations)

    @Slot(QProcess.ProcessError)
    def _relation_error(self, error: QProcess.ProcessError) -> None:
        self.relation_status.setText(
            "Unable to start Claim relation command."
            if error == QProcess.ProcessError.FailedToStart
            else f"Claim relation error: {error.name}"
        )

    def _apply_filter(self, text: str) -> None:
        terms = tuple(part for part in text.casefold().split() if part)
        for widget in (
            self.workspace.knowledge_list,
            self.workspace.claim_list,
            self.workspace.review_list,
        ):
            for index in range(widget.count()):
                item = widget.item(index)
                haystack = (item.text() + " " + item.toolTip()).casefold()
                item.setHidden(bool(terms) and not all(term in haystack for term in terms))
        self._sync_counts()

    @Slot()
    def _focus_filter(self) -> None:
        self.workspace.search_input.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self.workspace.search_input.selectAll()

    def _copy_text(self, value: str | None) -> None:
        if value:
            QApplication.clipboard().setText(value)
            self.workspace.browser_status.setText("Canonical entity ID copied.")

    def _copy_editor(self, editor: QPlainTextEdit) -> None:
        text = editor.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.workspace.browser_status.setText("Canonical detail text copied.")

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self._sync_counts)

    def _visible_count(self, widget: QListWidget) -> int:
        return sum(1 for index in range(widget.count()) if not widget.item(index).isHidden())

    def _sync_counts(self) -> None:
        if not hasattr(self, "counts"):
            return
        knowledge_total = self.workspace.knowledge_list.count()
        claim_total = self.workspace.claim_list.count()
        decision_total = self.workspace.review_list.count()
        visible = self._visible_count(
            (
                self.workspace.knowledge_list,
                self.workspace.claim_list,
                self.workspace.review_list,
            )[max(0, min(2, self.workspace.browser_tabs.currentIndex()))]
        )
        self.counts.setText(
            f"Knowledge {knowledge_total} · Claims {claim_total} · Decisions {decision_total} "
            f"· Visible {visible}"
        )


def install_canonical_memory_extensions(
    workspace: KnowledgeWorkspace,
) -> CanonicalMemoryExtension:
    """Attach progressive canonical-memory controls to the durable Knowledge workspace."""
    return CanonicalMemoryExtension(workspace)
