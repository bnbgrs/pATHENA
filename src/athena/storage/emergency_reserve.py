"""Physically allocated emergency disk reserve for ATHENA state recovery."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import fsync_directory, is_link_boundary

_MIB = 1024 * 1024
_GIB = 1024 * _MIB
_MIN_RESERVE_BYTES = 256 * _MIB
_MAX_RESERVE_BYTES = 1 * _GIB
_DEFAULT_WRITE_CHUNK_BYTES = 4 * _MIB


class EmergencyReserveError(RuntimeError):
    """Raised when the emergency reserve cannot be established safely."""


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer.")
    return value


def emergency_reserve_size_bytes(volume_size_bytes: int) -> int:
    """Return the Beta-03 default reserve size for a volume.

    The policy is ``max(256 MiB, min(1 GiB, 1% of volume size))``. The one-percent
    term is rounded up with integer arithmetic so the reserve never undershoots
    the policy because of truncation or float precision.
    """
    volume_size = _nonnegative_int(
        volume_size_bytes,
        "Emergency reserve volume_size_bytes",
    )
    one_percent = (volume_size + 99) // 100
    return max(_MIN_RESERVE_BYTES, min(_MAX_RESERVE_BYTES, one_percent))


def _assert_safe_parent(path: Path) -> None:
    cursor = path.parent
    while True:
        if is_link_boundary(cursor):
            raise EmergencyReserveError(
                "Emergency reserve path contains a symlink, junction, or reparse-point ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise EmergencyReserveError(
                "Emergency reserve path contains a non-directory ancestor."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _allocated_bytes(path: Path) -> int | None:
    """Return observable physical allocation when the platform reports it."""
    try:
        stat_result = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise EmergencyReserveError(
            "Emergency reserve allocation metadata could not be read."
        ) from exc
    blocks = getattr(stat_result, "st_blocks", None)
    if isinstance(blocks, int) and blocks >= 0:
        return blocks * 512
    return None


def _write_allocated_bytes(
    descriptor: int,
    *,
    size_bytes: int,
    chunk_bytes: int,
) -> None:
    """Allocate storage without relying on truncate-only sparse semantics."""
    posix_fallocate = getattr(os, "posix_fallocate", None)
    if callable(posix_fallocate):
        try:
            posix_fallocate(descriptor, 0, size_bytes)
            return
        except OSError:
            # Some filesystems/platform shims expose posix_fallocate but do not
            # support it. Fall back to explicit writes, which are non-sparse for
            # a newly created ordinary file unless the filesystem violates its
            # normal allocation semantics.
            pass

    remaining = size_bytes
    chunk = bytes(min(chunk_bytes, max(1, size_bytes)))
    while remaining:
        payload = chunk if remaining >= len(chunk) else chunk[:remaining]
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise EmergencyReserveError(
                    "Emergency reserve allocation write made no progress."
                )
            view = view[written:]
        remaining -= len(payload)


@dataclass(frozen=True, slots=True)
class EmergencyReserveStatus:
    path: Path
    required_bytes: int
    file_size_bytes: int
    allocated_bytes: int | None

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path) or not self.path.is_absolute():
            raise ValueError("Emergency reserve status path must be absolute.")
        required = _positive_int(
            self.required_bytes,
            "Emergency reserve required_bytes",
        )
        file_size = _nonnegative_int(
            self.file_size_bytes,
            "Emergency reserve file_size_bytes",
        )
        if file_size != required:
            raise ValueError(
                "Emergency reserve file size must exactly match required bytes."
            )
        if self.allocated_bytes is not None:
            allocated = _nonnegative_int(
                self.allocated_bytes,
                "Emergency reserve allocated_bytes",
            )
            if allocated < required:
                raise ValueError(
                    "Emergency reserve is sparse or under-allocated."
                )


class EmergencyReserveStore:
    """Own ``state_root/reserve/emergency.reserve`` without sparse allocation."""

    def __init__(self, state_root: Path) -> None:
        if not isinstance(state_root, Path):
            raise TypeError("Emergency reserve state_root must be a pathlib.Path.")
        root = state_root.expanduser()
        if not root.is_absolute():
            raise ValueError("Emergency reserve state_root must be absolute.")
        self.state_root = root
        self.reserve_root = root / "reserve"
        self.path = self.reserve_root / "emergency.reserve"

    def ensure(
        self,
        *,
        required_bytes: int,
        write_chunk_bytes: int = _DEFAULT_WRITE_CHUNK_BYTES,
    ) -> EmergencyReserveStatus:
        """Ensure one physically allocated reserve file of exactly the target size."""
        required = _positive_int(required_bytes, "Emergency reserve required_bytes")
        chunk_bytes = _positive_int(
            write_chunk_bytes,
            "Emergency reserve write_chunk_bytes",
        )
        _assert_safe_parent(self.path)
        if is_link_boundary(self.state_root) or not self.state_root.is_dir():
            raise EmergencyReserveError(
                "Emergency reserve state_root must be a real existing directory."
            )
        if self.reserve_root.exists():
            if is_link_boundary(self.reserve_root) or not self.reserve_root.is_dir():
                raise EmergencyReserveError(
                    "Emergency reserve directory is not a safe real directory."
                )
        else:
            try:
                self.reserve_root.mkdir(mode=0o700, parents=False, exist_ok=False)
                fsync_directory(self.state_root)
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve directory could not be created durably."
                ) from exc

        _assert_safe_parent(self.path)
        if is_link_boundary(self.path):
            raise EmergencyReserveError(
                "Emergency reserve file must not be a symlink, junction, or reparse point."
            )

        if self.path.exists():
            status = self.inspect(required_bytes=required)
            if status.file_size_bytes == required and (
                status.allocated_bytes is None or status.allocated_bytes >= required
            ):
                return status
            raise EmergencyReserveError(
                "Existing emergency reserve does not match the required physical allocation."
            )

        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = -1
        try:
            descriptor = os.open(self.path, flags, 0o600)
            try:
                path_stat = self.path.stat(follow_symlinks=False)
                handle_stat = os.fstat(descriptor)
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve file identity could not be verified."
                ) from exc
            if is_link_boundary(self.path) or not os.path.samestat(path_stat, handle_stat):
                raise EmergencyReserveError(
                    "Emergency reserve pathname changed during creation."
                )
            if os.name == "posix":
                os.fchmod(descriptor, 0o600)
            _write_allocated_bytes(
                descriptor,
                size_bytes=required,
                chunk_bytes=chunk_bytes,
            )
            os.fsync(descriptor)
        except BaseException:
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                descriptor = -1
            try:
                self.path.unlink(missing_ok=True)
                fsync_directory(self.reserve_root)
            except OSError:
                pass
            raise
        finally:
            if descriptor >= 0:
                os.close(descriptor)

        fsync_directory(self.reserve_root)
        return self.inspect(required_bytes=required)

    def inspect(self, *, required_bytes: int) -> EmergencyReserveStatus:
        required = _positive_int(required_bytes, "Emergency reserve required_bytes")
        _assert_safe_parent(self.path)
        if is_link_boundary(self.path) or not self.path.is_file():
            raise EmergencyReserveError(
                "Emergency reserve file is missing or unsafe."
            )
        try:
            file_size = self.path.stat(follow_symlinks=False).st_size
        except OSError as exc:
            raise EmergencyReserveError(
                "Emergency reserve file metadata could not be read."
            ) from exc
        allocated = _allocated_bytes(self.path)
        try:
            return EmergencyReserveStatus(
                path=self.path,
                required_bytes=required,
                file_size_bytes=file_size,
                allocated_bytes=allocated,
            )
        except ValueError as exc:
            raise EmergencyReserveError(str(exc)) from exc

    def release(self) -> int:
        """Delete only the reserve file, returning the logical bytes released."""
        _assert_safe_parent(self.path)
        if is_link_boundary(self.path):
            raise EmergencyReserveError(
                "Emergency reserve file path is unsafe and cannot be released automatically."
            )
        if not self.path.exists():
            return 0
        if not self.path.is_file():
            raise EmergencyReserveError(
                "Emergency reserve path is not a regular file."
            )
        try:
            size = self.path.stat(follow_symlinks=False).st_size
            self.path.unlink()
            fsync_directory(self.reserve_root)
        except OSError as exc:
            raise EmergencyReserveError(
                "Emergency reserve could not be released durably."
            ) from exc
        return size
