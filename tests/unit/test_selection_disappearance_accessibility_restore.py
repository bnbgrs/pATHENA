from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QListWidget

from athena.desktop.pathena_selection_disappearance_handoff import (
    _authoritative_list_description,
)


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def test_result_scope_replaces_stale_installation_fallback(qt_app: QApplication) -> None:
    selection = QListWidget()
    selection.setProperty(
        "pathenaResultScopeText",
        "Sources · 1 shown / 2 total · selected ABCDEF12",
    )

    assert _authoritative_list_description(selection, "stale install-time copy") == (
        "Sources · 1 shown / 2 total · selected ABCDEF12"
    )


def test_backup_scope_has_priority_over_generic_result_scope(qt_app: QApplication) -> None:
    selection = QListWidget()
    selection.setProperty(
        "pathenaResultScopeText",
        "Backup snapshots · 2 shown · selected 12345678",
    )
    selection.setProperty(
        "pathenaBackupListScope",
        "2 backup snapshots listed. Selected 12345678: state complete, "
        "verification verified deep, restore available.",
    )

    result = _authoritative_list_description(selection, "stale install-time copy")

    assert result.startswith("2 backup snapshots listed.")
    assert "restore available" in result


def test_installation_fallback_is_used_without_dynamic_scope(qt_app: QApplication) -> None:
    selection = QListWidget()

    assert _authoritative_list_description(selection, "initial description") == (
        "initial description"
    )
