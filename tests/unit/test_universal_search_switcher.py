from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem

from athena.api.search_contracts import SearchProtectionResponse, SearchResultResponse
from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.universal_switcher import UniversalSearchSwitcher


class _SearchController(QObject):
    search_ready = Signal(int, str, object)
    search_failed = Signal(int, str, str)

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, int]] = []
        self._request_id = 0

    def search(self, query: str, *, limit: int = 30) -> int:
        self.calls.append((query, limit))
        self._request_id += 1
        return self._request_id


def _app() -> QApplication:
    return create_application(["pathena-universal-switcher-test"])


def _result(
    entity_type: str,
    entity_id: str,
    *,
    title: str = "Alpha result",
    preview: str = "Alpha durable content.",
    rank: int = 1,
) -> SearchResultResponse:
    return SearchResultResponse(
        result_ref=f"{entity_type}:{entity_id}",
        title=title,
        preview=preview,
        entity_type=entity_type,
        revision_id=(
            "22222222-2222-2222-2222-222222222222"
            if entity_type in {"knowledge", "claim", "chat_message"}
            else None
        ),
        rank=rank,
        retrieval_methods=("lexical",),
        source_anchor=None,
        protection=SearchProtectionResponse(
            state="unprotected",
            protection_scope_id=None,
        ),
    )


def _surface() -> tuple[
    QApplication,
    PathenaMainWindow,
    _SearchController,
    UniversalSearchSwitcher,
]:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = _SearchController()
    switcher = UniversalSearchSwitcher(
        window,
        controller,  # type: ignore[arg-type]
    )
    window.show()
    app.processEvents()
    return app, window, controller, switcher


def test_switcher_dispatches_normalized_core_search_and_ignores_stale_results() -> None:
    app, window, controller, switcher = _surface()
    try:
        switcher.open()
        app.processEvents()
        assert switcher.dialog.isVisible()
        assert switcher.query.hasFocus()

        switcher.query.setText("  alpha   project  ")
        switcher._debounce.stop()
        switcher._dispatch_search()

        assert controller.calls == [("alpha project", 40)]
        assert switcher._latest_request_id == 1
        assert "Searching local pATHENA" in switcher.status.text()

        stale = _result(
            "knowledge",
            "11111111-1111-1111-1111-111111111111",
            title="Stale result",
        )
        controller.search_ready.emit(99, "alpha project", (stale,))
        app.processEvents()
        assert switcher.results.count() == 0

        current = _result(
            "knowledge",
            "33333333-3333-3333-3333-333333333333",
        )
        controller.search_ready.emit(1, "alpha project", (current,))
        app.processEvents()

        assert switcher.results.count() == 1
        item = switcher.results.item(0)
        assert item.data(Qt.ItemDataRole.UserRole) == current.result_ref
        assert "KNOWLEDGE  Alpha result" in item.text()
        assert switcher.results.accessibleDescription().startswith(
            "1 universal search result."
        )
        assert switcher.status.text() == "1 result from local pATHENA Core."
    finally:
        switcher.deleteLater()
        window.close()
        app.processEvents()


def test_switcher_query_change_invalidates_inflight_delivery() -> None:
    app, window, controller, switcher = _surface()
    try:
        switcher.open()
        switcher.query.setText("alpha")
        switcher._debounce.stop()
        switcher._dispatch_search()
        assert switcher._latest_request_id == 1

        switcher.query.setText("beta")
        assert switcher._latest_request_id is None
        assert switcher.results.count() == 0

        controller.search_ready.emit(
            1,
            "alpha",
            (
                _result(
                    "source",
                    "11111111-1111-1111-1111-111111111111",
                ),
            ),
        )
        app.processEvents()

        assert switcher.results.count() == 0
        assert "Ready to search" in switcher.status.text()
    finally:
        switcher.deleteLater()
        window.close()
        app.processEvents()


def test_switcher_renders_empty_and_real_error_states_without_fake_results() -> None:
    app, window, controller, switcher = _surface()
    try:
        switcher.open()
        switcher.query.setText("missing")
        switcher._debounce.stop()
        switcher._dispatch_search()

        controller.search_ready.emit(1, "missing", ())
        app.processEvents()
        assert switcher.results.count() == 0
        assert switcher.status.text() == (
            "No matches for “missing”. Try a broader local search."
        )
        assert switcher.dialog.property("pathenaUiState") == "empty"

        switcher.query.setText("offline")
        switcher._debounce.stop()
        switcher._dispatch_search()
        controller.search_failed.emit(
            2,
            "offline",
            "ATHENA Core is unavailable.",
        )
        app.processEvents()

        assert switcher.results.count() == 0
        assert switcher.status.text() == (
            "Search unavailable · ATHENA Core is unavailable."
        )
        assert switcher.dialog.property("pathenaUiState") == "error"
    finally:
        switcher.deleteLater()
        window.close()
        app.processEvents()


def test_switcher_opens_loaded_source_by_stable_entity_id() -> None:
    app, window, controller, switcher = _surface()
    source_id = "55555555-5555-5555-5555-555555555555"
    source_list = QListWidget(window)
    source_list.setObjectName("sourceList")
    unrelated = QListWidgetItem("Other")
    unrelated.setData(
        Qt.ItemDataRole.UserRole,
        "66666666-6666-6666-6666-666666666666",
    )
    target = QListWidgetItem("Target")
    target.setData(Qt.ItemDataRole.UserRole, source_id)
    source_list.addItem(unrelated)
    source_list.addItem(target)

    try:
        switcher.open()
        switcher.query.setText("source alpha")
        switcher._debounce.stop()
        switcher._dispatch_search()
        result = _result("source", source_id)
        controller.search_ready.emit(1, "source alpha", (result,))
        app.processEvents()

        switcher.results.setCurrentRow(0)
        switcher._activate_current()
        app.processEvents()

        assert window.navigation.currentRow() == 4
        assert source_list.currentItem() is target
        assert not switcher.dialog.isVisible()
    finally:
        switcher.deleteLater()
        source_list.deleteLater()
        window.close()
        app.processEvents()


@pytest.mark.parametrize(
    ("entity_type", "expected_row"),
    [
        ("chat_message", 0),
        ("research_result", 2),
    ],
)
def test_switcher_parentless_results_navigate_without_faking_exact_selection(
    entity_type: str,
    expected_row: int,
) -> None:
    app, window, _controller, switcher = _surface()
    try:
        switcher.open()
        result = _result(
            entity_type,
            "77777777-7777-7777-7777-777777777777",
        )

        switcher._open_result(result)
        app.processEvents()

        assert window.navigation.currentRow() == expected_row
        assert not switcher.dialog.isVisible()
    finally:
        switcher.deleteLater()
        window.close()
        app.processEvents()


def test_switcher_owns_ctrl_p_without_changing_ctrl_k_command_palette() -> None:
    _app_instance, window, _controller, switcher = _surface()
    try:
        assert switcher.shortcut.key().toString(
            QKeySequence.SequenceFormat.PortableText
        ) == "Ctrl+P"
        assert switcher.query.placeholderText().startswith(
            "Search chats, knowledge, claims"
        )
        assert "Ctrl K for commands" in switcher.dialog.findChildren(
            type(switcher.status)
        )[-1].text()
    finally:
        switcher.deleteLater()
        window.close()



def test_switcher_and_command_palette_are_mutually_exclusive() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    commands = CommandPaletteController(window)
    controller = _SearchController()
    switcher = UniversalSearchSwitcher(
        window,
        controller,  # type: ignore[arg-type]
    )
    try:
        window.show()
        app.processEvents()

        commands.open()
        app.processEvents()
        assert commands.dialog.isVisible()

        switcher.open()
        app.processEvents()
        assert switcher.dialog.isVisible()
        assert not commands.dialog.isVisible()

        commands.open()
        app.processEvents()
        assert commands.dialog.isVisible()
        assert not switcher.dialog.isVisible()
    finally:
        switcher.deleteLater()
        commands.deleteLater()
        window.close()
        app.processEvents()



def test_switcher_keeps_unresolved_deep_link_explanation_visible() -> None:
    app, window, controller, switcher = _surface()
    source_list = QListWidget(window)
    source_list.setObjectName("sourceList")
    source_list.addItem(QListWidgetItem("Different loaded source"))
    source_list.item(0).setData(
        Qt.ItemDataRole.UserRole,
        "88888888-8888-8888-8888-888888888888",
    )
    missing_source_id = "99999999-9999-9999-9999-999999999999"

    try:
        switcher.open()
        switcher.query.setText("missing source")
        switcher._debounce.stop()
        switcher._dispatch_search()
        controller.search_ready.emit(
            1,
            "missing source",
            (_result("source", missing_source_id),),
        )
        app.processEvents()

        switcher._activate_current()
        app.processEvents()

        assert window.navigation.currentRow() == 4
        assert switcher.dialog.isVisible()
        assert switcher.status.text() == (
            "Opened the owning workspace. The exact result is not loaded in "
            "its current list yet."
        )
        assert source_list.currentItem() is None
    finally:
        switcher.deleteLater()
        source_list.deleteLater()
        window.close()
        app.processEvents()
