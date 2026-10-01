from __future__ import annotations

from pathlib import Path
import pytest
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QFileDialog

import athena.desktop.files_workspace as files_workspace_module
from athena.desktop.files_workspace import FilesWorkspace


class _TextSurface:
    def __init__(self) -> None:
        self.value = ""

    def clear(self) -> None:
        self.value = ""

    def setText(self, value: str) -> None:
        self.value = value

    def setPlainText(self, value: str) -> None:
        self.value = value


class _QueueHarness:
    _source_label = staticmethod(FilesWorkspace._source_label)

    def __init__(self) -> None:
        self._operation = ""
        self._operation_source_id: str | None = None
        self._buffer = ""
        self._selected_source_id: str | None = None
        self._pending_imports: list[str] = []
        self._active_import_path: str | None = None
        self.process_busy = False
        self.details = _TextSurface()
        self.status = _TextSurface()
        self.starts: list[tuple[str, list[str], str, str | None]] = []
        self.sync_calls = 0

    def _busy(self) -> bool:
        return self.process_busy

    def _sync_controls(self, *, force_disabled: bool = False) -> None:
        del force_disabled
        self.sync_calls += 1

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
        self.starts.append((operation, arguments, label, source_id))

    def _start_next_import(self) -> None:
        FilesWorkspace._start_next_import(self)  # type: ignore[arg-type]

    def _resume_import_queue(self) -> bool:
        if not self._pending_imports:
            return False
        self._start_next_import()
        return True

    def _drain_output(self) -> None:
        return

    def _operation_owns_details(self) -> bool:
        return self._operation_source_id == self._selected_source_id

    def import_paths(self, paths: list[str]) -> None:
        FilesWorkspace.import_paths(self, paths)  # type: ignore[arg-type]


@pytest.fixture(autouse=True)
def _disable_qt_state_styling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        files_workspace_module,
        "set_pathena_ui_state",
        lambda *_args, **_kwargs: None,
    )


def _touch(path: Path, text: str = "content") -> str:
    path.write_text(text, encoding="utf-8")
    return str(path.absolute())


def test_import_paths_deduplicates_and_starts_first_file(tmp_path: Path) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.txt")
    missing = str(tmp_path / "missing.pdf")

    harness.import_paths([first, first, missing, second])

    assert harness.starts == [
        (
            "import",
            ["import", first],
            "Capturing first.md · 1 more queued",
            None,
        )
    ]
    assert harness._active_import_path == first
    assert harness._pending_imports == [second]


def test_import_paths_waits_for_existing_process_before_starting(tmp_path: Path) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    harness.process_busy = True

    harness.import_paths([first, second])

    assert harness.starts == []
    assert harness._pending_imports == [first, second]

    harness.process_busy = False
    harness._start_next_import()

    assert harness.starts == [
        (
            "import",
            ["import", first],
            "Capturing first.md · 1 more queued",
            None,
        )
    ]
    assert harness._active_import_path == first
    assert harness._pending_imports == [second]


def test_successful_import_continues_queue_without_intermediate_refresh(
    tmp_path: Path,
) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")
    captured = "11111111-1111-1111-1111-111111111111"
    refreshes: list[bool] = []

    harness._operation = "import"
    harness._operation_source_id = None
    harness._selected_source_id = None
    harness._active_import_path = first
    harness._pending_imports = [second]
    harness._buffer = f"SOURCE_CAPTURED {captured}\nPROCESS_QUEUED\n"
    setattr(harness, "refresh", lambda: refreshes.append(True))
    FilesWorkspace._process_finished(
        harness,  # type: ignore[arg-type]
        0,
        QProcess.ExitStatus.NormalExit,
    )

    assert harness._selected_source_id == captured
    assert harness._active_import_path == second
    assert harness._pending_imports == []
    assert harness.starts == [
        (
            "import",
            ["import", second],
            "Capturing second.md",
            captured,
        )
    ]
    assert refreshes == []


def test_failed_import_continues_with_next_queued_file(tmp_path: Path) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")

    harness._operation = "import"
    harness._operation_source_id = None
    harness._active_import_path = first
    harness._pending_imports = [second]
    harness._buffer = "synthetic failure"

    FilesWorkspace._process_finished(
        harness,  # type: ignore[arg-type]
        7,
        QProcess.ExitStatus.NormalExit,
    )

    assert "failed" in harness.status.value.casefold()
    assert harness._active_import_path == second
    assert harness._pending_imports == []
    assert harness.starts == [
        (
            "import",
            ["import", second],
            "Capturing second.md",
            None,
        )
    ]


def test_process_start_error_continues_with_next_queued_file(tmp_path: Path) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.md")

    harness._operation = "import"
    harness._operation_source_id = None
    harness._active_import_path = first
    harness._pending_imports = [second]

    FilesWorkspace._process_error(
        harness,  # type: ignore[arg-type]
        QProcess.ProcessError.FailedToStart,
    )

    assert "unable to start" in harness.status.value.casefold()
    assert harness._active_import_path == second
    assert harness._pending_imports == []
    assert harness.starts == [
        (
            "import",
            ["import", second],
            "Capturing second.md",
            None,
        )
    ]


def test_file_picker_allows_multiple_files_and_delegates_to_queue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _QueueHarness()
    first = _touch(tmp_path / "first.md")
    second = _touch(tmp_path / "second.pdf")
    queued: list[list[str]] = []

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileNames",
        lambda *_args, **_kwargs: ([first, second], ""),
    )
    setattr(harness, "import_paths", lambda paths: queued.append(paths))

    FilesWorkspace._choose_file(harness)  # type: ignore[arg-type]

    assert queued == [[first, second]]
