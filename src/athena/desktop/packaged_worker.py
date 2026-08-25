"""Hidden Windows worker entry point for packaged pATHENA process roles."""

from __future__ import annotations

import ctypes
import os
import sys
from collections.abc import Sequence
from typing import TextIO

from athena.desktop.packaged_app import (
    PackagedInvocationError,
    PackagedTarget,
    route_packaged_argv,
)

_STD_INPUT_HANDLE = -10
_STD_OUTPUT_HANDLE = -11
_STD_ERROR_HANDLE = -12
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def _windows_standard_stream(std_handle: int, mode: str) -> TextIO:
    """Recover an inherited Win32 pipe for a no-console PyInstaller worker."""
    import msvcrt

    kernel32 = ctypes.windll.kernel32
    kernel32.GetStdHandle.argtypes = [ctypes.c_ulong]
    kernel32.GetStdHandle.restype = ctypes.c_void_p
    handle = kernel32.GetStdHandle(ctypes.c_ulong(std_handle).value)
    if handle in (None, 0, _INVALID_HANDLE_VALUE):
        return open(os.devnull, mode, encoding="utf-8")

    flags = os.O_RDONLY if "r" in mode else os.O_WRONLY
    descriptor = msvcrt.open_osfhandle(int(handle), flags)
    buffering = -1 if "r" in mode else 1
    return os.fdopen(
        descriptor,
        mode,
        buffering=buffering,
        encoding="utf-8",
        errors="replace",
    )


def restore_packaged_standard_streams() -> None:
    """Restore only inherited pipes; otherwise use devnull without opening a console."""
    if os.name != "nt":
        return
    if sys.stdin is None:
        sys.stdin = _windows_standard_stream(_STD_INPUT_HANDLE, "r")
    if sys.stdout is None:
        sys.stdout = _windows_standard_stream(_STD_OUTPUT_HANDLE, "w")
    if sys.stderr is None:
        sys.stderr = _windows_standard_stream(_STD_ERROR_HANDLE, "w")


def dispatch_worker(argv: Sequence[str] | None = None) -> int:
    restore_packaged_standard_streams()
    raw_arguments = tuple(sys.argv[1:] if argv is None else argv)
    try:
        invocation = route_packaged_argv(raw_arguments)
    except PackagedInvocationError as exc:
        print(f"pATHENA worker error: {exc}", file=sys.stderr)
        return 2

    if invocation.target is PackagedTarget.DESKTOP:
        print("pATHENA worker refuses a desktop invocation.", file=sys.stderr)
        return 2

    if invocation.target is PackagedTarget.CORE:
        from athena.api.process import main as core_main

        return core_main(invocation.arguments)

    if invocation.target is PackagedTarget.ATHENA_CLI:
        from athena.__main__ import main as athena_main

        return athena_main(invocation.arguments)

    if invocation.target is PackagedTarget.JOBS_CLI:
        from athena.desktop.jobs_cli import main as jobs_main

        return jobs_main(invocation.arguments)

    if invocation.target is PackagedTarget.HARDWARE_ACCEPTANCE:
        from athena.hardware_acceptance import main as hardware_acceptance_main

        return hardware_acceptance_main(invocation.arguments)

    raise RuntimeError(f"Unsupported packaged worker target: {invocation.target!r}")


def main(argv: Sequence[str] | None = None) -> int:
    return dispatch_worker(argv)


if __name__ == "__main__":
    raise SystemExit(main())
