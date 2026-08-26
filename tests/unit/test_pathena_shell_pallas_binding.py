from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.app import create_application
from athena.desktop.ascii_panel import AsciiPanel
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-shell-pallas-binding-test"])


def test_shell_binds_optional_pallas_semantic_root_once(monkeypatch: pytest.MonkeyPatch) -> None:
    roots: list[QWidget | None] = []

    def bind_semantic_root(_panel: AsciiPanel, root: QWidget | None) -> None:
        roots.append(root)

    monkeypatch.setattr(
        AsciiPanel,
        "bind_semantic_root",
        bind_semantic_root,
        raising=False,
    )

    app = _app()
    window = PathenaMainWindow(api_controller=None)
    app.processEvents()
    try:
        assert roots == [window]
    finally:
        window.close()
        app.processEvents()


def test_shell_remains_compatible_before_core_owner_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(AsciiPanel, "bind_semantic_root", raising=False)

    app = _app()
    window = PathenaMainWindow(api_controller=None)
    app.processEvents()
    try:
        assert window.ascii_panel is not None
    finally:
        window.close()
        app.processEvents()
