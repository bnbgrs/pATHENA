"""Runtime filesystem bootstrap service."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from athena.storage.locality import ActiveStateLocalityError, assert_active_state_root_local
from athena.storage.paths import RuntimePaths


class RuntimePathError(RuntimeError):
    """Raised when required local runtime storage is unusable."""


def _require_path(path: object) -> Path:
    if not isinstance(path, Path):
        raise TypeError("ATHENA runtime path must be a pathlib.Path.")
    return path


def _reject_symlink_ancestors(path: Path) -> None:
    """Reject existing symlink components before creating or probing state."""
    cursor = path.parent
    while True:
        if cursor.is_symlink():
            raise RuntimePathError(
                f"ATHENA runtime path has a symlink ancestor: {str(cursor)!r}."
            )
        if cursor.exists() and not cursor.is_dir():
            raise RuntimePathError(
                f"ATHENA runtime path ancestor is not a directory: {str(cursor)!r}."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


class RuntimeLayoutService:
    """Create and validate ATHENA's required local runtime directories.

    Stopping this service never deletes data. Runtime directories can contain
    non-reconstructible state, so cleanup belongs to explicit maintenance
    operations rather than application shutdown.
    """

    name = "runtime-layout"

    def __init__(self, paths: RuntimePaths) -> None:
        if not isinstance(paths, RuntimePaths):
            raise TypeError("paths must be a RuntimePaths instance.")
        self.paths = paths

    def start(self) -> None:
        try:
            assert_active_state_root_local(self.paths.state_root)
        except ActiveStateLocalityError as exc:
            raise RuntimePathError(str(exc)) from exc

        for directory in self.paths.required_local_directories:
            self._ensure_directory(directory)

        self._verify_writable(self.paths.state_root)
        self._verify_writable(self.paths.spool_root)
        self._verify_writable(self.paths.derived_root)
        self._verify_writable(self.paths.log_root)
        self._verify_writable(self.paths.temp_root)

    def stop(self) -> None:
        # Deliberately a no-op: persistent state must survive application stop.
        return

    @staticmethod
    def _ensure_directory(path: Path) -> None:
        validated = _require_path(path)
        _reject_symlink_ancestors(validated)
        if validated.is_symlink():
            raise RuntimePathError(
                f"ATHENA runtime directory must not be a symlink: {str(validated)!r}."
            )
        try:
            validated.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimePathError(
                f"Cannot create ATHENA runtime directory {str(validated)!r}."
            ) from exc

        _reject_symlink_ancestors(validated)
        if validated.is_symlink() or not validated.is_dir():
            raise RuntimePathError(
                f"ATHENA runtime path is not a safe directory: {str(validated)!r}."
            )

    @staticmethod
    def _verify_writable(path: Path) -> None:
        validated = _require_path(path)
        _reject_symlink_ancestors(validated)
        if validated.is_symlink() or not validated.is_dir():
            raise RuntimePathError(
                f"ATHENA runtime path is not a safe directory: {str(validated)!r}."
            )
        probe = validated / f".athena-write-probe-{os.getpid()}-{secrets.token_hex(4)}"

        try:
            with probe.open("xb") as handle:
                handle.write(b"ATHENA")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise RuntimePathError(
                f"ATHENA runtime directory is not writable: {str(validated)!r}."
            ) from exc
        finally:
            try:
                probe.unlink(missing_ok=True)
            except OSError as exc:
                # A failed probe cleanup is itself evidence that the directory
                # is not healthy enough for durable ATHENA state.
                if probe.exists():
                    raise RuntimePathError(
                        f"ATHENA could not clean its write probe in {str(validated)!r}."
                    ) from exc
