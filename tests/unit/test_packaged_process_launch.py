from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from athena.desktop.supervisor import core_process_launch_spec


def test_frozen_windows_core_launch_uses_dispatcher_executable_directly() -> None:
    launch = core_process_launch_spec(
        executable=r"C:\Program Files\pATHENA\pATHENA.exe",
        base_executable=r"C:\Python312\python.exe",
        platform="win32",
        frozen=True,
    )

    assert launch.program == r"C:\Program Files\pATHENA\pATHENA.exe"
    assert launch.arguments == ("-m", "athena.api.process")
    assert launch.venv_launcher is None


def test_nonfrozen_windows_venv_behavior_remains_unchanged() -> None:
    launch = core_process_launch_spec(
        executable=r"C:\workspace\.venv\Scripts\python.exe",
        base_executable=r"C:\Python312\python.exe",
        platform="win32",
        frozen=False,
    )

    assert launch.program == r"C:\Python312\python.exe"
    assert launch.arguments == ("-m", "athena.api.process")
    assert launch.venv_launcher == r"C:\workspace\.venv\Scripts\python.exe"
