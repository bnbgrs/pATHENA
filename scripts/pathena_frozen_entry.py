"""Fail-closed PyInstaller entry point for the pATHENA Windows test executable.

The frozen binary doubles as the desktop shell and the explicit child-process roles
already launched by pATHENA. Unknown argv must never fall through to another desktop
window: doing so can turn one unexpected child invocation into a process storm.
"""

from __future__ import annotations

import ctypes
import json
import multiprocessing
import os
import sys
import tempfile
import traceback
from collections.abc import Sequence
from pathlib import Path

_BUILD_SOURCE_SHA = "d14aca9504021bdacadb89dc478ca41545ab4316"
_DESKTOP_MUTEX_NAME = "Local\\pATHENA-Desktop-Singleton"
_ERROR_ALREADY_EXISTS = 183
_DESKTOP_MUTEX_HANDLE: int | None = None


def _trace_role(role: str, arguments: Sequence[str]) -> None:
    trace_root = os.getenv("ATHENA_FROZEN_TRACE_DIR", "").strip()
    if not trace_root:
        return
    try:
        root = Path(trace_root)
        root.mkdir(parents=True, exist_ok=True)
        payload = {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "role": role,
            "argv": list(arguments),
        }
        (root / f"{os.getpid()}-{role}.json").write_text(
            json.dumps(payload, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        # Diagnostic tracing must never change runtime behavior.
        pass


def _failure_log_path() -> Path:
    local_root = os.getenv("ATHENA_LOCAL_ROOT", "").strip()
    if local_root:
        return Path(local_root) / "logs" / f"frozen-startup-{os.getpid()}.log"
    local_app_data = os.getenv("LOCALAPPDATA", "").strip()
    if local_app_data:
        return (
            Path(local_app_data)
            / "ATHENA"
            / "logs"
            / f"frozen-startup-{os.getpid()}.log"
        )
    return Path(tempfile.gettempdir()) / f"pathena-frozen-startup-{os.getpid()}.log"


def _write_fatal_error() -> None:
    try:
        path = _failure_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "pATHENA frozen startup failure\n"
            f"build_source_sha={_BUILD_SOURCE_SHA}\n"
            f"pid={os.getpid()} ppid={os.getppid()}\n"
            f"argv={sys.argv!r}\n\n"
            + traceback.format_exc(),
            encoding="utf-8",
        )
    except OSError:
        pass


def _acquire_desktop_singleton() -> bool:
    """Return True only for the one process allowed to own the desktop window."""
    global _DESKTOP_MUTEX_HANDLE
    if os.name != "nt":
        return True

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_mutex = kernel32.CreateMutexW
    create_mutex.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p)
    create_mutex.restype = ctypes.c_void_p

    handle = create_mutex(None, 0, _DESKTOP_MUTEX_NAME)
    if not handle:
        raise OSError(ctypes.get_last_error(), "CreateMutexW failed")
    _DESKTOP_MUTEX_HANDLE = int(handle)
    return ctypes.get_last_error() != _ERROR_ALREADY_EXISTS


def _run_core(arguments: Sequence[str]) -> int:
    _trace_role("core", arguments)
    from athena.api.process import main as core_main

    return core_main(arguments)


def _scheduler_role(arguments: Sequence[str]) -> str:
    if len(arguments) >= 2 and arguments[:2] == ["job", "scheduler-run"]:
        try:
            lane_index = arguments.index("--lane")
            lane = arguments[lane_index + 1]
        except (ValueError, IndexError):
            return "scheduler-unknown"
        return f"scheduler-{lane}"
    return "cli"


def _run_cli(arguments: Sequence[str]) -> int:
    _trace_role(_scheduler_role(arguments), arguments)
    from athena.__main__ import main as cli_main

    return cli_main(arguments)


def _run_metadata_smoke() -> int:
    from importlib.metadata import version

    pypdf_version = version("pypdf")
    from athena.core.application import AthenaApplication  # noqa: F401
    from athena.source.pdf_representation_service import (  # noqa: F401
        SourcePdfRepresentationService,
    )

    print(f"pypdf={pypdf_version}")
    return 0


def _run_desktop() -> int:
    if not _acquire_desktop_singleton():
        _trace_role("desktop-duplicate-blocked", ())
        return 0
    _trace_role("desktop", ())
    from athena.desktop.app import main as desktop_main

    return desktop_main([sys.argv[0]])


def _reject_unknown(arguments: Sequence[str]) -> int:
    _trace_role("rejected-unknown", arguments)
    # Windowed builds have no reliable stderr. The trace/fatal log is the diagnostic
    # surface; the important safety property is that this path never opens a desktop.
    return 64


def main() -> int:
    # PyInstaller/multiprocessing may consume its own frozen worker invocation here.
    # Any invocation that returns from freeze_support() still has to pass the explicit
    # role allow-list below.
    multiprocessing.freeze_support()
    arguments = sys.argv[1:]

    if not arguments:
        return _run_desktop()
    if arguments[:2] == ["-m", "athena.api.process"]:
        return _run_core(arguments[2:])
    if arguments[:2] == ["-m", "athena"]:
        return _run_cli(arguments[2:])
    if arguments == ["--pathena-build-info"]:
        print(f"pATHENA Windows R3 test build from {_BUILD_SOURCE_SHA}")
        return 0
    if arguments == ["--pathena-metadata-smoke"]:
        return _run_metadata_smoke()
    return _reject_unknown(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:
        _write_fatal_error()
        raise
