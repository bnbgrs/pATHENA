from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QWidget

from athena.desktop.pathena_background_completion_accessibility import (
    BackgroundCompletionAccessibility,
    _Target,
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


def _target(selected: list[str | None]) -> tuple[_Target, QLabel, QWidget, QListWidget]:
    status = QLabel("Completed.")
    details = QWidget()
    selection = QListWidget()
    target = _Target(
        status=status,
        details=details,
        selection=selection,
        selected_id=lambda: selected[0],
        noun="Source",
    )
    return target, status, details, selection


def test_background_owner_is_exposed_in_accessible_status(qt_app: QApplication) -> None:
    selected: list[str | None] = ["22222222-2222-2222-2222-222222222222"]
    target, status, details, _selection = _target(selected)
    details.setProperty(
        "pathenaBackgroundOperationOwner",
        "11111111-1111-1111-1111-111111111111",
    )

    controller = BackgroundCompletionAccessibility((target,))

    assert status.property("pathenaBackgroundAccessibleOwner").startswith("11111111")
    assert "Background Source operation belongs to 11111111" in status.accessibleDescription()
    assert "Current selection remains 22222222" in status.accessibleDescription()
    controller.deleteLater()


def test_current_owner_uses_normal_status_description(qt_app: QApplication) -> None:
    selected: list[str | None] = ["33333333-3333-3333-3333-333333333333"]
    target, status, details, _selection = _target(selected)
    details.setProperty("pathenaBackgroundOperationOwner", selected[0])

    controller = BackgroundCompletionAccessibility((target,))

    assert status.accessibleName() == "Source status"
    assert status.accessibleDescription() == "Completed."
    assert status.property("pathenaBackgroundAccessibleOwner") == ""
    controller.deleteLater()


def test_status_text_change_refreshes_background_announcement(qt_app: QApplication) -> None:
    selected: list[str | None] = [None]
    target, status, details, _selection = _target(selected)
    details.setProperty("pathenaBackgroundOperationOwner", "import")
    controller = BackgroundCompletionAccessibility((target,))

    status.setText("Source captured in the background.")

    assert "No current selection is active" in status.accessibleDescription()
    assert "Source captured in the background" in status.accessibleDescription()
    controller.deleteLater()
