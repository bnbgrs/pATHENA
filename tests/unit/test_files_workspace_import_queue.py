from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QFileDialog

from athena.desktop.app import create_application
from athena.desktop.files_workspace import FilesWorkspace


def _app() -> QApplication:
    return create_application(["athena-files-import-queue-test"])


def _workspace(monkeypatch: object) -> tuple[QApplication, FilesWorkspace]:
    monkeypatch.setattr(FilesWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = FilesWorkspace()
    workspace._refresh_timer.stop()
    return app, workspace


def _touch(path: Path, text: str = "content") -> str:
    path.write_text(text, encoding="utf-8")
    return str(path.absolute())


def test_import_paths_deduplicates_and_starts_first_file(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.txt")
    missing = str(tmp_path / "missing.pdf")
    starts: list[tuple[str, list[str], str, str | None]] = []

    def fake_start(
        operation: str,
        arguments: list[str],
        label: str,
        *,
        source_id: str | None = None,
    ) -> None:
        workspace._operation = operation
        workspace._operation_source_id = source_id
        starts.append((operation, arguments, label, source_id))

    monkeypatch.setattr(workspace, "_start", fake_start)

    try:
        workspace.import_paths([first, first, missing, second])

        assert starts == [
            (
                "import",
                ["import", first],
                "Capturing first.md · 1 more queued",
                None,
            )
        ]
        assert workspace._active_import_path == first
        assert workspace._pending_imports == [second]
        assert not workspace.import_button.isEnabled()
        assert not workspace.refresh_button.isEnabled()
        assert not workspace.process_button.isEnabled()
    finally:
        workspace.close()


def test_import_paths_waits_for_existing_process_before_starting(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    busy = True
    starts: list[list[str]] = []

    monkeypatch.setattr(workspace, "_busy", lambda: busy)
    monkeypatch.setattr(
        workspace,
        "_start",
        lambda _operation, arguments, _label, **_kwargs: starts.append(arguments),
    )

    try:
        workspace.import_paths([first, second])

        assert starts == []
        assert workspace._pending_imports == [first, second]

        busy = False
        workspace._start_next_import()

        assert starts == [["import", first]]
        assert workspace._active_import_path == first
        assert workspace._pending_imports == [second]
    finally:
        workspace.close()


def test_successful_import_continues_queue_without_intermediate_refresh(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    captured = "11111111-1111-1111-1111-111111111111"
    starts: list[list[str]] = []
    refreshes: list[bool] = []

    workspace._operation = "import"
    workspace._operation_source_id = None
    workspace._selected_source_id = None
    workspace._active_import_path = first
    workspace._pending_imports = [second]
    workspace._buffer = f"SOURCE_CAPTURED {captured}\nPROCESS_QUEUED\n"

    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    monkeypatch.setattr(workspace, "refresh", lambda: refreshes.append(True))
    monkeypatch.setattr(
        workspace,
        "_start",
        lambda _operation, arguments, _label, **_kwargs: starts.append(arguments),
    )

    def resume_now() -> bool:
        if not workspace._pending_imports:
            return False
        workspace._start_next_import()
        return True

    monkeypatch.setattr(workspace, "_resume_import_queue", resume_now)

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace._selected_source_id == captured
        assert workspace._active_import_path == second
        assert workspace._pending_imports == []
        assert starts == [["import", second]]
        assert refreshes == []
    finally:
        workspace.close()


def test_failed_import_continues_with_next_queued_file(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    starts: list[list[str]] = []

    workspace._operation = "import"
    workspace._operation_source_id = None
    workspace._active_import_path = first
    workspace._pending_imports = [second]
    workspace._buffer = "synthetic failure"
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    monkeypatch.setattr(
        workspace,
        "_start",
        lambda _operation, arguments, _label, **_kwargs: starts.append(arguments),
    )

    def resume_now() -> bool:
        if not workspace._pending_imports:
            return False
        workspace._start_next_import()
        return True

    monkeypatch.setattr(workspace, "_resume_import_queue", resume_now)

    try:
        workspace._process_finished(7, QProcess.ExitStatus.NormalExit)

        assert "failed" in workspace.status.text().casefold()
        assert workspace._active_import_path == second
        assert workspace._pending_imports == []
        assert starts == [["import", second]]
    finally:
        workspace.close()


def test_process_start_error_continues_with_next_queued_file(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    starts: list[list[str]] = []

    workspace._operation = "import"
    workspace._operation_source_id = None
    workspace._active_import_path = first
    workspace._pending_imports = [second]
    monkeypatch.setattr(
        workspace,
        "_start",
        lambda _operation, arguments, _label, **_kwargs: starts.append(arguments),
    )

    def resume_now() -> bool:
        if not workspace._pending_imports:
            return False
        workspace._start_next_import()
        return True

    monkeypatch.setattr(workspace, "_resume_import_queue", resume_now)

    try:
        workspace._process_error(QProcess.ProcessError.FailedToStart)

        assert "unable to start" in workspace.status.text().casefold()
        assert workspace._active_import_path == second
        assert starts == [["import", second]]
    finally:
        workspace.close()


def test_file_picker_allows_multiple_files_and_delegates_to_queue(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    _app_instance, workspace = _workspace(monkeypatch)
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.pdf")
    queued: list[list[str]] = []

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileNames",
        lambda *_args, **_kwargs: ([first, second], ""),
    )
    monkeypatch.setattr(workspace, "import_paths", lambda paths: queued.append(paths))

    try:
        workspace._choose_file()

        assert queued == [[first, second]]
    finally:
        workspace.close()
