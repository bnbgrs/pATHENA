"""Core-backed Ctrl+P universal search for the pATHENA desktop."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QVBoxLayout,
)

from athena.api.search_contracts import SearchResultResponse

if TYPE_CHECKING:
    from athena.desktop.api_controller import DesktopApiController
    from athena.desktop.window import AthenaMainWindow


_DEBOUNCE_MS = 180
_RESULT_LIMIT = 40
_ENTITY_LABELS = {
    "knowledge": "KNOWLEDGE",
    "claim": "CLAIM",
    "chat_message": "CHAT",
    "research_result": "RESEARCH",
    "source": "SOURCE",
    "job": "JOB",
}
_NAVIGATION_ROWS = {
    "chat_message": 0,
    "knowledge": 1,
    "claim": 1,
    "research_result": 2,
    "job": 3,
    "source": 4,
}
_LIST_TARGETS = {
    "knowledge": ("persistentKnowledgeList", 0),
    "claim": ("persistentClaimList", 1),
    "job": ("durableJobList", None),
    "source": ("sourceList", None),
}


class UniversalSearchSwitcher(QObject):
    """Search durable Core entities without maintaining a second UI index."""

    def __init__(
        self,
        window: AthenaMainWindow,
        controller: DesktopApiController,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.controller = controller
        self._latest_request_id: int | None = None
        self._latest_query = ""
        self._results_by_ref: dict[str, SearchResultResponse] = {}

        self.dialog = QDialog(window)
        self.dialog.setObjectName("universalSearchDialog")
        self.dialog.setWindowTitle("pATHENA Search")
        self.dialog.setAccessibleName("pATHENA universal search")
        self.dialog.setAccessibleDescription(
            "Search chats, knowledge, claims, research results, sources, and jobs "
            "through the local pATHENA Core."
        )
        self.dialog.setModal(False)
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.dialog.setMinimumWidth(720)
        self.dialog.resize(760, 560)

        self.query = QLineEdit(self.dialog)
        # Reuse the established V3 command-surface roles without reusing the
        # command palette's behavior or result index.
        self.query.setObjectName("commandPaletteQuery")
        self.query.setPlaceholderText(
            "Search chats, knowledge, claims, research, sources, and jobs…"
        )
        self.query.setAccessibleName("Universal search")
        self.query.setAccessibleDescription(
            "Type a local search query. Results come from the pATHENA Core, not "
            "from a separate desktop index."
        )

        self.results = QListWidget(self.dialog)
        self.results.setObjectName("commandPaletteResults")
        self.results.setAccessibleName("Universal search results")
        self.results.setAccessibleDescription(
            "No universal search has been run yet."
        )
        self.results.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.results.setMinimumHeight(350)

        self.status = QLabel("Type to search local pATHENA data.", self.dialog)
        self.status.setObjectName("commandPaletteFooter")
        self.status.setWordWrap(True)
        self.status.setAccessibleName("Universal search status")

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(_DEBOUNCE_MS)
        self._debounce.timeout.connect(self._dispatch_search)

        self._build_dialog()

        self.shortcut = QShortcut(QKeySequence("Ctrl+P"), window)
        self.shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut.activated.connect(self.open)

        self._down_shortcut = QShortcut(QKeySequence("Down"), self.dialog)
        self._down_shortcut.activated.connect(lambda: self._move_selection(1))
        self._up_shortcut = QShortcut(QKeySequence("Up"), self.dialog)
        self._up_shortcut.activated.connect(lambda: self._move_selection(-1))
        self._escape_shortcut = QShortcut(QKeySequence("Esc"), self.dialog)
        self._escape_shortcut.activated.connect(self.dialog.hide)

        self.query.textChanged.connect(self._query_changed)
        self.query.returnPressed.connect(self._activate_current)
        self.results.itemActivated.connect(self._activate_item)
        controller.search_ready.connect(self._search_ready)
        controller.search_failed.connect(self._search_failed)

        self._peer_dialogs = tuple(
            dialog
            for name in ("commandPalette", "helpDialog")
            if (dialog := window.findChild(QDialog, name)) is not None
        )
        for dialog in self._peer_dialogs:
            dialog.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            event.type() == QEvent.Type.Show
            and watched in self._peer_dialogs
            and self.dialog.isVisible()
        ):
            self.dialog.hide()
        return super().eventFilter(watched, event)

    def _build_dialog(self) -> None:
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Search pATHENA")
        title.setObjectName("commandPaletteTitle")
        title.setBuddy(self.query)
        hint = QLabel("Ctrl P")
        hint.setObjectName("commandPaletteHint")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(hint)

        footer = QLabel(
            "Enter to open  ·  Esc to close  ·  ↑↓ to move  ·  Ctrl K for commands"
        )
        footer.setObjectName("commandPaletteFooter")

        layout.addLayout(header)
        layout.addWidget(self.query)
        layout.addWidget(self.status)
        layout.addWidget(self.results, 1)
        layout.addWidget(footer)

    def open(self) -> None:
        """Open centered over the desktop and invalidate earlier result deliveries."""
        for dialog in self._peer_dialogs:
            if dialog.isVisible():
                dialog.hide()
        self._debounce.stop()
        self._latest_request_id = None
        self._latest_query = ""
        self.query.clear()
        self.results.clear()
        self._results_by_ref.clear()
        self._set_status(
            "Type to search local pATHENA data.",
            state="idle",
        )

        parent_rect = self.window.geometry()
        size = self.dialog.size()
        x = parent_rect.x() + max(0, (parent_rect.width() - size.width()) // 2)
        y = parent_rect.y() + max(
            0,
            min(160, (parent_rect.height() - size.height()) // 3),
        )
        self.dialog.move(x, y)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        self.query.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _query_changed(self, text: str) -> None:
        self._debounce.stop()
        normalized = _normalize_query(text)
        self._latest_request_id = None
        self._latest_query = normalized
        self.results.clear()
        self._results_by_ref.clear()

        if not normalized:
            self._set_status(
                "Type to search local pATHENA data.",
                state="idle",
            )
            return

        self._set_status(
            "Ready to search local pATHENA data…",
            state="pending",
        )
        self._debounce.start()

    @Slot()
    def _dispatch_search(self) -> None:
        query = _normalize_query(self.query.text())
        if not query or query != self._latest_query:
            return
        try:
            request_id = self.controller.search(
                query,
                limit=_RESULT_LIMIT,
            )
        except (TypeError, ValueError) as exc:
            self._set_status(str(exc), state="error")
            return

        self._latest_request_id = request_id
        self._set_status(
            f"Searching local pATHENA for “{query}”…",
            state="busy",
        )

    @Slot(int, str, object)
    def _search_ready(
        self,
        request_id: int,
        query: str,
        payload: object,
    ) -> None:
        if not self._is_current_delivery(request_id, query):
            return
        if not isinstance(payload, tuple) or not all(
            isinstance(item, SearchResultResponse) for item in payload
        ):
            self.results.clear()
            self._set_status(
                "Search returned an invalid result contract.",
                state="error",
            )
            return

        self.results.clear()
        self._results_by_ref = {
            result.result_ref: result
            for result in payload
        }
        for result in payload:
            self.results.addItem(_result_item(result))

        count = self.results.count()
        if count:
            self.results.setCurrentRow(0)
            noun = "result" if count == 1 else "results"
            self._set_status(
                f"{count} {noun} from local pATHENA Core.",
                state="ready",
            )
            self.results.setAccessibleDescription(
                f"{count} universal search {noun}. Use Up and Down to move, "
                "then Enter to open the selected result."
            )
        else:
            self._set_status(
                f"No matches for “{query}”. Try a broader local search.",
                state="empty",
            )
            self.results.setAccessibleDescription(
                f"No universal search results for {query}."
            )

    @Slot(int, str, str)
    def _search_failed(
        self,
        request_id: int,
        query: str,
        message: str,
    ) -> None:
        if not self._is_current_delivery(request_id, query):
            return
        self.results.clear()
        self._results_by_ref.clear()
        self._set_status(
            f"Search unavailable · {message}",
            state="error",
        )
        self.results.setAccessibleDescription(
            "Universal search is currently unavailable."
        )

    def _is_current_delivery(self, request_id: int, query: str) -> bool:
        return (
            self.dialog.isVisible()
            and request_id == self._latest_request_id
            and _normalize_query(query) == self._latest_query
            and _normalize_query(self.query.text()) == self._latest_query
        )

    def _set_status(self, text: str, *, state: str) -> None:
        self.status.setText(text)
        self.status.setAccessibleDescription(text)
        self.dialog.setProperty("pathenaUiState", state)
        self.results.setProperty("pathenaUiState", state)

    def _move_selection(self, delta: int) -> None:
        count = self.results.count()
        if count <= 0:
            return
        row = self.results.currentRow()
        if row < 0:
            row = 0
        self.results.setCurrentRow((row + delta) % count)

    def _activate_current(self) -> None:
        item = self.results.currentItem()
        if item is not None:
            self._activate_item(item)

    @Slot(QListWidgetItem)
    def _activate_item(self, item: QListWidgetItem) -> None:
        result_ref = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(result_ref, str):
            return
        result = self._results_by_ref.get(result_ref)
        if result is None:
            return
        self._open_result(result)

    def _open_result(self, result: SearchResultResponse) -> None:
        row = _NAVIGATION_ROWS.get(result.entity_type)
        if row is None:
            self._set_status(
                "This search result type is not navigable in the current desktop.",
                state="error",
            )
            return

        self.window.navigation.setCurrentRow(row)
        entity_id = _result_entity_id(result)

        target = _LIST_TARGETS.get(result.entity_type)
        selected = False
        if target is not None:
            list_name, tab_index = target
            if tab_index is not None:
                tabs = self.window.findChild(QTabWidget, "canonicalMemoryTabs")
                if tabs is not None and 0 <= tab_index < tabs.count():
                    tabs.setCurrentIndex(tab_index)
            listing = self.window.findChild(QListWidget, list_name)
            if listing is not None:
                selected = _select_stable_id(listing, entity_id)

        # ChatMessage and ResearchResult currently do not expose their parent
        # chat/job identity in SearchResultResponse. Navigation is therefore
        # intentionally limited to the owning workspace instead of guessing.
        if target is None or selected:
            self.dialog.hide()
            return

        # The stable entity is real but the current workspace page may not have
        # loaded it yet. Keep the switcher visible and explain that the deep
        # selection did not complete instead of silently pretending success.
        self._set_status(
            "Opened the owning workspace. The exact result is not loaded in "
            "its current list yet.",
            state="ready",
        )
        self.query.setFocus(Qt.FocusReason.ShortcutFocusReason)


def _normalize_query(text: str) -> str:
    return " ".join(text.split())


def _result_entity_id(result: SearchResultResponse) -> str:
    prefix, separator, value = result.result_ref.partition(":")
    if (
        not separator
        or prefix != result.entity_type
        or not value
    ):
        return result.result_ref
    return value


def _result_item(result: SearchResultResponse) -> QListWidgetItem:
    entity_label = _ENTITY_LABELS.get(
        result.entity_type,
        result.entity_type.upper(),
    )
    title = _normalize_query(result.title or "")
    preview = _normalize_query(result.preview)
    if not title:
        title = preview or result.result_ref

    body = preview
    if body == title:
        body = ""
    if len(body) > 180:
        body = body[:177].rstrip() + "…"

    text = f"{entity_label}  {title}"
    if body:
        text += f"\n{body}"

    item = QListWidgetItem(text)
    item.setData(Qt.ItemDataRole.UserRole, result.result_ref)
    item.setData(Qt.ItemDataRole.UserRole + 1, result.revision_id)
    item.setData(Qt.ItemDataRole.UserRole + 2, result.entity_type)
    item.setToolTip(
        f"{result.result_ref}\n"
        f"retrieval={', '.join(result.retrieval_methods)}\n"
        f"protection={result.protection.state}"
    )
    item.setData(
        Qt.ItemDataRole.AccessibleTextRole,
        f"{entity_label} {title}",
    )
    description = body or "No preview text."
    item.setData(
        Qt.ItemDataRole.AccessibleDescriptionRole,
        f"{description} Rank {result.rank}.",
    )
    return item


def _select_stable_id(listing: QListWidget, entity_id: str) -> bool:
    for index in range(listing.count()):
        item = listing.item(index)
        if str(item.data(Qt.ItemDataRole.UserRole) or "") != entity_id:
            continue
        listing.setCurrentItem(item)
        listing.scrollToItem(item)
        listing.setFocus(Qt.FocusReason.ShortcutFocusReason)
        return True
    return False


def install_universal_search_switcher(
    window: AthenaMainWindow,
    controller: DesktopApiController,
) -> UniversalSearchSwitcher:
    """Install the Core-backed Ctrl+P search without changing Ctrl+K commands."""
    switcher = UniversalSearchSwitcher(window, controller)
    window.setProperty("pathenaUniversalSearchSwitcher", switcher)
    window.setProperty("pathenaUniversalSearchManaged", True)
    return switcher
