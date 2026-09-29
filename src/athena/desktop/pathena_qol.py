"""Cross-workspace quality-of-life controls for the pATHENA desktop."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from PySide6.QtCore import QByteArray, QEvent, QObject, QSettings, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.lmstudio_runtime import LMStudioRuntimeController
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.research_workspace import ResearchWorkspace

_SETTINGS_ROOT: Final = "desktop/qol/v1"
_NAV_LABELS: Final = (
    "Workspace",
    "Library",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)


@dataclass(frozen=True, slots=True)
class _QuickAction:
    label: str
    search_text: str
    kind: str
    target: str


def _default_settings() -> QSettings:
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "pATHENA",
        "pATHENA",
    )


class PathenaQolController(QObject):
    """Persist work state and expose fast navigation, recovery and activity UI."""

    activity_message = Signal(str)

    def __init__(
        self,
        window: PathenaMainWindow,
        controller: DesktopApiController,
        *,
        runtime: LMStudioRuntimeController,
        files_workspace: FilesWorkspace,
        research_workspace: ResearchWorkspace,
        jobs_workspace: JobsWorkspace,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.controller = controller
        self.runtime = runtime
        self.files_workspace = files_workspace
        self.research_workspace = research_workspace
        self.jobs_workspace = jobs_workspace
        self.settings = settings or _default_settings()
        self._last_snapshot: DesktopApiSnapshot | None = None
        self._restored_model = False
        self._restored_chat = False
        self._focus_mode = False
        self._focus_previous: tuple[bool, bool] | None = None
        self._quick_actions: list[_QuickAction] = []
        self._last_failed_prompt = ""
        self._last_failed_operation = ""
        self._zoom_delta = 0
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(250)
        self._save_timer.timeout.connect(self._save_transient_state)

        self._previous_clean_exit = self._read_bool("clean_exit", True)
        self.settings.setValue(f"{_SETTINGS_ROOT}/clean_exit", False)
        self.settings.sync()

        self._build_quick_switcher()
        self._build_activity_center()
        self._install_context_actions()
        self._install_shortcuts()
        self._restore_immediate_state()
        self._connect_signals()

        window.setAcceptDrops(True)
        window.installEventFilter(self)
        window.prompt_input.installEventFilter(self)
        QTimer.singleShot(0, self._refresh_activity)

    def _read_bool(self, key: str, default: bool) -> bool:
        return bool(self.settings.value(f"{_SETTINGS_ROOT}/{key}", default, type=bool))

    def _read_int(self, key: str, default: int) -> int:
        return int(self.settings.value(f"{_SETTINGS_ROOT}/{key}", default, type=int))

    def _read_str(self, key: str, default: str = "") -> str:
        value = self.settings.value(f"{_SETTINGS_ROOT}/{key}", default)
        return value if isinstance(value, str) else default

    def _build_quick_switcher(self) -> None:
        self.quick_dialog = QDialog(self.window)
        self.quick_dialog.setObjectName("quickSwitcher")
        self.quick_dialog.setWindowTitle("Quick Switcher")
        self.quick_dialog.setModal(False)
        self.quick_dialog.setMinimumWidth(620)

        layout = QVBoxLayout(self.quick_dialog)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.quick_query = QLineEdit()
        self.quick_query.setObjectName("quickSwitcherQuery")
        self.quick_query.setPlaceholderText(
            "Jump to a workspace, conversation, or local model…"
        )
        self.quick_query.setAccessibleName("Quick switcher search")
        layout.addWidget(self.quick_query)

        self.quick_results = QListWidget()
        self.quick_results.setObjectName("quickSwitcherResults")
        self.quick_results.setMinimumHeight(320)
        layout.addWidget(self.quick_results)

        self.quick_query.textChanged.connect(self._render_quick_results)
        self.quick_query.returnPressed.connect(self._activate_quick_current)
        self.quick_results.itemActivated.connect(self._activate_quick_item)

        self._quick_escape = QShortcut(QKeySequence("Esc"), self.quick_dialog)
        self._quick_escape.activated.connect(self.quick_dialog.hide)
        self._quick_down = QShortcut(QKeySequence("Down"), self.quick_dialog)
        self._quick_down.activated.connect(lambda: self._move_quick_selection(1))
        self._quick_up = QShortcut(QKeySequence("Up"), self.quick_dialog)
        self._quick_up.activated.connect(lambda: self._move_quick_selection(-1))

    def _build_activity_center(self) -> None:
        dock = QDockWidget("Activity", self.window)
        dock.setObjectName("activityCenter")
        dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("What pATHENA is doing")
        title.setObjectName("settingsRuntimeTitle")
        header.addWidget(title)
        header.addStretch(1)
        self.activity_refresh = QPushButton("Refresh")
        self.activity_refresh.setObjectName("newChatButton")
        self.activity_refresh.clicked.connect(self._refresh_activity)
        header.addWidget(self.activity_refresh)
        layout.addLayout(header)

        self.activity_list = QListWidget()
        self.activity_list.setObjectName("activityList")
        self.activity_list.setAccessibleName("Current pATHENA activity")
        layout.addWidget(self.activity_list)
        dock.setWidget(panel)
        self.window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        dock.hide()
        self.activity_dock = dock

        self.activity_timer = QTimer(self)
        self.activity_timer.setInterval(1_000)
        self.activity_timer.timeout.connect(self._refresh_activity)
        dock.visibilityChanged.connect(self._activity_visibility_changed)

    def _install_context_actions(self) -> None:
        composer = self.window.findChild(QFrame, "composer")
        layout = composer.layout() if composer is not None else None
        if not isinstance(layout, QHBoxLayout):
            return

        self.retry_button = QPushButton("Retry")
        self.retry_button.setObjectName("newChatButton")
        self.retry_button.setToolTip("Retry the last failed send without losing the draft")
        self.retry_button.hide()
        self.retry_button.clicked.connect(self.retry_last_send)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setObjectName("newChatButton")
        self.continue_button.setToolTip("Ask the selected model to continue the current answer")
        self.continue_button.hide()
        self.continue_button.clicked.connect(self.continue_chat)

        send_index = layout.indexOf(self.window.send_button)
        insert_at = send_index if send_index >= 0 else layout.count()
        layout.insertWidget(insert_at, self.retry_button)
        layout.insertWidget(insert_at + 1, self.continue_button)

    def _install_shortcuts(self) -> None:
        self.quick_shortcut = QShortcut(QKeySequence("Ctrl+P"), self.window)
        self.quick_shortcut.activated.connect(self.open_quick_switcher)

        self.activity_shortcut = QShortcut(QKeySequence("Ctrl+J"), self.window)
        self.activity_shortcut.activated.connect(self.toggle_activity_center)

        self.inspector_shortcut = QShortcut(QKeySequence("Ctrl+I"), self.window)
        self.inspector_shortcut.activated.connect(self.toggle_inspector)

        self.sidebar_shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), self.window)
        self.sidebar_shortcut.activated.connect(self.toggle_sidebar)

        self.focus_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self.window)
        self.focus_shortcut.activated.connect(self.toggle_focus_mode)

        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self.window)
        self.zoom_in_shortcut.activated.connect(lambda: self._change_zoom(1))
        self.zoom_in_equal_shortcut = QShortcut(QKeySequence("Ctrl+="), self.window)
        self.zoom_in_equal_shortcut.activated.connect(lambda: self._change_zoom(1))
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self.window)
        self.zoom_out_shortcut.activated.connect(lambda: self._change_zoom(-1))
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self.window)
        self.zoom_reset_shortcut.activated.connect(self._reset_zoom)

        self.knowledge_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self.window)
        self.knowledge_shortcut.activated.connect(self.add_latest_to_knowledge)

    def _connect_signals(self) -> None:
        self.controller.snapshot_ready.connect(self.apply_snapshot)
        self.controller.chat_loaded.connect(self._chat_committed)
        self.controller.chat_sent.connect(self._chat_committed)
        self.controller.grounded_chat_sent.connect(self._grounded_chat_committed)
        self.controller.chat_operation_failed.connect(self._chat_failed)
        self.controller.chat_busy_changed.connect(self._chat_busy_changed)

        self.runtime.status_changed.connect(self._runtime_activity)
        self.runtime.busy_changed.connect(lambda _busy: self._refresh_activity())

        self.window.prompt_input.textChanged.connect(self._schedule_save)
        self.window.navigation.currentRowChanged.connect(self._page_changed)
        self.window.model_selector.activated.connect(self._model_changed)
        self.window.settings_model_selector.activated.connect(self._model_changed)
        self.window.ground_button.toggled.connect(self._schedule_save)

        self.activity_message.connect(self._runtime_activity)

    def _restore_immediate_state(self) -> None:
        geometry = self.settings.value(f"{_SETTINGS_ROOT}/geometry")
        if isinstance(geometry, QByteArray) and not geometry.isEmpty():
            self.window.restoreGeometry(geometry)

        page = self._read_int("page", 0)
        if 0 <= page < self.window.navigation.count():
            self.window.navigation.setCurrentRow(page)

        self.window.ground_button.setChecked(self._read_bool("grounded", False))
        draft = self._read_str("draft")
        if draft:
            self.window.prompt_input.setText(draft)
            if not self._previous_clean_exit:
                self.activity_message.emit("Recovered unsent chat draft after an unclean exit.")

        self._zoom_delta = max(-4, min(8, self._read_int("zoom_delta", 0)))
        if self._zoom_delta:
            self._apply_zoom()

    @Slot(object)
    def apply_snapshot(self, value: object) -> None:
        if not isinstance(value, DesktopApiSnapshot):
            return
        self._last_snapshot = value

        if not self._restored_model:
            stored_model = self._read_str("model_id")
            if stored_model:
                index = self.window.model_selector.findData(stored_model)
                if index >= 0:
                    self.window.model_selector.setCurrentIndex(index)
                    self.window._on_model_selected(index)
            selected_model = self.window._selected_model()
            if selected_model is not None:
                self.settings.setValue(
                    f"{_SETTINGS_ROOT}/model_id",
                    selected_model.backend_model_id,
                )
                if self.runtime.auto_load.isChecked():
                    self.runtime.ensure_selected_model()
            self._restored_model = True

        if not self._restored_chat:
            stored_chat = self._read_str("chat_id")
            if stored_chat:
                index = self.window.chat_selector.findData(stored_chat)
                if index >= 0:
                    self.window.chat_selector.setCurrentIndex(index)
                    self.window._on_chat_selected(index)
            self._restored_chat = True

        self._rebuild_quick_actions()
        self._refresh_activity()

    def _rebuild_quick_actions(self) -> None:
        actions: list[_QuickAction] = []
        for index, label in enumerate(_NAV_LABELS):
            actions.append(
                _QuickAction(
                    label=f"Workspace · {label}",
                    search_text=f"workspace {label}".casefold(),
                    kind="workspace",
                    target=str(index),
                )
            )

        snapshot = self._last_snapshot
        if snapshot is not None:
            for chat in snapshot.chats:
                started = datetime.fromtimestamp(chat.started_at_us / 1_000_000)
                label = (
                    f"Conversation · {started:%d %b %H:%M} · "
                    f"{chat.message_count} messages · {chat.chat_id[:8]}"
                )
                actions.append(
                    _QuickAction(
                        label=label,
                        search_text=f"conversation chat {chat.chat_id} {label}".casefold(),
                        kind="chat",
                        target=chat.chat_id,
                    )
                )
            for model in snapshot.models:
                if model.model_type != "llm":
                    continue
                state = "loaded" if model.loaded else "available"
                label = f"Model · {model.display_name} · {state}"
                actions.append(
                    _QuickAction(
                        label=label,
                        search_text=f"model {model.backend_model_id} {label}".casefold(),
                        kind="model",
                        target=model.backend_model_id,
                    )
                )
        self._quick_actions = actions
        if self.quick_dialog.isVisible():
            self._render_quick_results(self.quick_query.text())

    @Slot()
    def open_quick_switcher(self) -> None:
        self._rebuild_quick_actions()
        self.quick_query.clear()
        self._render_quick_results("")
        self.quick_dialog.adjustSize()
        self.quick_dialog.show()
        self.quick_dialog.raise_()
        self.quick_dialog.activateWindow()
        self.quick_query.setFocus()

    @Slot(str)
    def _render_quick_results(self, query: str) -> None:
        terms = tuple(term for term in query.casefold().split() if term)
        self.quick_results.clear()
        shown = 0
        for index, action in enumerate(self._quick_actions):
            if terms and not all(term in action.search_text for term in terms):
                continue
            item = QListWidgetItem(action.label)
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.quick_results.addItem(item)
            shown += 1
            if shown >= 80:
                break
        if self.quick_results.count():
            self.quick_results.setCurrentRow(0)

    def _move_quick_selection(self, delta: int) -> None:
        count = self.quick_results.count()
        if count == 0:
            return
        row = self.quick_results.currentRow()
        self.quick_results.setCurrentRow(max(0, min(count - 1, row + delta)))

    @Slot()
    def _activate_quick_current(self) -> None:
        item = self.quick_results.currentItem()
        if item is not None:
            self._activate_quick_item(item)

    @Slot(QListWidgetItem)
    def _activate_quick_item(self, item: QListWidgetItem) -> None:
        raw_index = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(raw_index, int) or not 0 <= raw_index < len(self._quick_actions):
            return
        action = self._quick_actions[raw_index]
        self.quick_dialog.hide()

        if action.kind == "workspace":
            self.window.navigation.setCurrentRow(int(action.target))
        elif action.kind == "chat":
            index = self.window.chat_selector.findData(action.target)
            if index >= 0:
                self.window.chat_selector.setCurrentIndex(index)
                self.window._on_chat_selected(index)
        elif action.kind == "model":
            index = self.window.model_selector.findData(action.target)
            if index >= 0:
                self.window.model_selector.setCurrentIndex(index)
                self.window._on_model_selected(index)
                self.settings.setValue(f"{_SETTINGS_ROOT}/model_id", action.target)
                self.runtime.ensure_selected_model()

    @Slot(bool)
    def _activity_visibility_changed(self, visible: bool) -> None:
        if visible:
            self._refresh_activity()
            self.activity_timer.start()
        else:
            self.activity_timer.stop()

    @Slot()
    def toggle_activity_center(self) -> None:
        self.activity_dock.setVisible(not self.activity_dock.isVisible())

    @Slot()
    def _refresh_activity(self) -> None:
        rows: list[str] = []
        snapshot = self._last_snapshot
        if snapshot is None:
            rows.append("Core · connecting")
        else:
            rows.append(f"Core · {snapshot.health.core_status}")
            provider = snapshot.provider.status if snapshot.provider is not None else "unavailable"
            rows.append(f"Model provider · {provider} · {snapshot.resolved_model_freshness}")
            selected = self.window._selected_model()
            if selected is not None:
                state = "loaded" if selected.loaded else "available / loading on use"
                context = selected.loaded_context_length or selected.context_capacity
                context_text = f" · context {context:,}" if context is not None else ""
                rows.append(f"Model · {selected.display_name} · {state}{context_text}")
            rows.append(
                f"Conversations · {len(snapshot.chats)} · {snapshot.resolved_chat_freshness}"
            )

        rows.append(self.runtime.status_text)

        research_status = self.research_workspace.status.text().strip()
        if research_status:
            rows.append(f"Research · {research_status}")
        jobs_status = self.jobs_workspace.status.text().strip()
        if jobs_status:
            rows.append(f"Jobs · {jobs_status}")
        source_status = self.files_workspace.status.text().strip()
        if source_status:
            rows.append(f"Sources · {source_status}")

        if not self._previous_clean_exit and self._read_str("draft"):
            rows.append("Recovery · unsent draft restored from previous unclean exit")

        self.activity_list.clear()
        for row in rows:
            self.activity_list.addItem(row)

    @Slot(str)
    def _runtime_activity(self, _message: str) -> None:
        if self.activity_dock.isVisible():
            self._refresh_activity()

    @Slot()
    def retry_last_send(self) -> None:
        if not self._last_failed_prompt or self.window._chat_busy:
            return
        self.window.prompt_input.setText(self._last_failed_prompt)
        self.window.ground_button.setChecked(self._last_failed_operation == "send_grounded")
        self.retry_button.hide()
        self.window._submit_prompt()

    @Slot()
    def continue_chat(self) -> None:
        if self.window._chat_busy or not self.window._core_ready:
            return
        self.window.prompt_input.setText("Continue.")
        self.window._submit_prompt()

    @Slot(str, str)
    def _chat_failed(self, operation: str, _message: str) -> None:
        if operation not in {"send", "send_grounded"}:
            return
        prompt = self.window.prompt_input.text().strip()
        if not prompt:
            return
        self._last_failed_prompt = prompt
        self._last_failed_operation = operation
        self.retry_button.show()
        self.continue_button.hide()
        self._refresh_activity()

    @Slot(bool)
    def _chat_busy_changed(self, busy: bool) -> None:
        if busy:
            prompt = self.window.prompt_input.text().strip()
            if prompt:
                self.settings.setValue(f"{_SETTINGS_ROOT}/last_prompt", prompt)
                self.settings.sync()
            self.retry_button.hide()
            self.continue_button.hide()
        self._refresh_activity()

    @Slot(object)
    def _chat_committed(self, thread: object) -> None:
        chat_id = getattr(thread, "chat_id", None)
        if isinstance(chat_id, str):
            self.settings.setValue(f"{_SETTINGS_ROOT}/chat_id", chat_id)
            self.settings.sync()
        self._last_failed_prompt = ""
        self.retry_button.hide()
        self.continue_button.show()

    @Slot(object)
    def _grounded_chat_committed(self, response: object) -> None:
        thread = getattr(response, "thread", None)
        self._chat_committed(thread)

    @Slot(int)
    def _page_changed(self, index: int) -> None:
        self.settings.setValue(f"{_SETTINGS_ROOT}/page", index)
        self._schedule_save()

    @Slot(int)
    def _model_changed(self, _index: int) -> None:
        model_id = self.window._selected_model_id()
        if model_id:
            self.settings.setValue(f"{_SETTINGS_ROOT}/model_id", model_id)
            self.settings.sync()

    @Slot()
    def _schedule_save(self, *_args: object) -> None:
        self._save_timer.start()

    @Slot()
    def _save_transient_state(self) -> None:
        self.settings.setValue(f"{_SETTINGS_ROOT}/draft", self.window.prompt_input.text())
        self.settings.setValue(
            f"{_SETTINGS_ROOT}/grounded", self.window.ground_button.isChecked()
        )
        self.settings.setValue(f"{_SETTINGS_ROOT}/page", self.window.navigation.currentRow())
        self.settings.setValue(f"{_SETTINGS_ROOT}/geometry", self.window.saveGeometry())
        self.settings.setValue(f"{_SETTINGS_ROOT}/zoom_delta", self._zoom_delta)
        self.settings.sync()

    @Slot()
    def toggle_inspector(self) -> None:
        inspector = self.window.findChild(QFrame, "inspector")
        if inspector is not None:
            inspector.setVisible(not inspector.isVisible())

    @Slot()
    def toggle_sidebar(self) -> None:
        rail = self.window.findChild(QFrame, "iconRail")
        if rail is not None:
            rail.setVisible(not rail.isVisible())

    @Slot()
    def toggle_focus_mode(self) -> None:
        inspector = self.window.findChild(QFrame, "inspector")
        rail = self.window.findChild(QFrame, "iconRail")
        if inspector is None or rail is None:
            return
        if not self._focus_mode:
            self._focus_previous = (inspector.isVisible(), rail.isVisible())
            inspector.hide()
            rail.hide()
            self._focus_mode = True
        else:
            previous = self._focus_previous or (True, True)
            inspector.setVisible(previous[0])
            rail.setVisible(previous[1])
            self._focus_mode = False

    def _change_zoom(self, delta: int) -> None:
        self._zoom_delta = max(-4, min(8, self._zoom_delta + delta))
        self._apply_zoom()
        self._schedule_save()

    @Slot()
    def _reset_zoom(self) -> None:
        self._zoom_delta = 0
        self._apply_zoom()
        self._schedule_save()

    def _apply_zoom(self) -> None:
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return
        font = app.font()
        base_size = 10
        font.setPointSize(max(7, base_size + self._zoom_delta))
        app.setFont(font)
        self.window.setProperty("pathenaZoomPercent", 100 + self._zoom_delta * 10)

    @Slot()
    def add_latest_to_knowledge(self) -> None:
        buttons = self.window.chat_messages_widget.findChildren(
            QPushButton, "addKnowledgeButton"
        )
        for button in reversed(buttons):
            if button.isEnabled():
                button.click()
                return

    def _restore_last_prompt(self) -> bool:
        if self.window.prompt_input.text():
            return False
        last_prompt = self._read_str("last_prompt")
        if not last_prompt:
            return False
        self.window.prompt_input.setText(last_prompt)
        return True

    def _drop_paths(self, event: QDropEvent) -> list[str]:
        paths: list[str] = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                local = url.toLocalFile()
                if local:
                    paths.append(local)
        return paths

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.window:
            if isinstance(event, QDragEnterEvent):
                if any(url.isLocalFile() for url in event.mimeData().urls()):
                    event.acceptProposedAction()
                    return True
            elif isinstance(event, QDropEvent):
                paths = self._drop_paths(event)
                if paths:
                    self.files_workspace.import_paths(paths)
                    self.window.navigation.setCurrentRow(4)
                    self.activity_message.emit(
                        f"Queued {len(paths)} dropped file(s) for Source import."
                    )
                    event.acceptProposedAction()
                    return True
            elif event.type() == QEvent.Type.WindowActivate:
                selected_model = self.window._selected_model()
                if (
                    selected_model is not None
                    and not selected_model.loaded
                    and self.runtime.auto_load.isChecked()
                ):
                    self.runtime.ensure_selected_model()
            elif event.type() in {QEvent.Type.Move, QEvent.Type.Resize}:
                self._schedule_save()
            elif event.type() == QEvent.Type.Close:
                self._save_transient_state()
                self.settings.setValue(f"{_SETTINGS_ROOT}/clean_exit", True)
                self.settings.sync()

        if watched is self.window.prompt_input and isinstance(event, QKeyEvent):
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Up:
                if self._restore_last_prompt():
                    return True
        return super().eventFilter(watched, event)


def install_pathena_qol(
    window: PathenaMainWindow,
    controller: DesktopApiController,
    *,
    runtime: LMStudioRuntimeController,
    files_workspace: FilesWorkspace,
    research_workspace: ResearchWorkspace,
    jobs_workspace: JobsWorkspace,
) -> PathenaQolController:
    return PathenaQolController(
        window,
        controller,
        runtime=runtime,
        files_workspace=files_workspace,
        research_workspace=research_workspace,
        jobs_workspace=jobs_workspace,
    )
