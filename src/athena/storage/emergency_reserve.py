"""Physically allocated emergency disk reserve for ATHENA state recovery."""

from __future__ import annotations

import os
import shutil
import stat
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import durable_mkdir, fsync_directory, is_link_boundary

_MIB = 1024 * 1024
_GIB = 1024 * _MIB
_MIN_RESERVE_BYTES = 256 * _MIB
_MAX_RESERVE_BYTES = 1 * _GIB
_DEFAULT_WRITE_CHUNK_BYTES = 4 * _MIB
_RESERVE_FILENAME = "emergency.reserve"
_CONCURRENT_CREATION_TIMEOUT_SECONDS = 30.0
_CONCURRENT_CREATION_STAGNANT_SECONDS = 0.5
_CONCURRENT_CREATION_POLL_SECONDS = 0.05


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


def _allocated_bytes_from_stat(stat_result: os.stat_result) -> int | None:
    blocks = getattr(stat_result, "st_blocks", None)
    if isinstance(blocks, int) and blocks >= 0:
        return blocks * 512
    return None


def _allocated_bytes(path: Path) -> int | None:
    """Return observable physical allocation when the platform reports it."""
    try:
        stat_result = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise EmergencyReserveError(
            "Emergency reserve allocation metadata could not be read."
        ) from exc
    return _allocated_bytes_from_stat(stat_result)


def _open_posix_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise EmergencyReserveError(
            "Emergency reserve directory could not be opened safely."
        ) from exc
    try:
        handle_stat = os.fstat(descriptor)
        path_stat = os.stat(path, follow_symlinks=False)
        if not stat.S_ISDIR(handle_stat.st_mode) or not os.path.samestat(
            handle_stat,
            path_stat,
        ):
            raise EmergencyReserveError(
                "Emergency reserve directory identity changed while opening."
            )
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _assert_posix_directory_current(path: Path, descriptor: int) -> None:
    try:
        handle_stat = os.fstat(descriptor)
        path_stat = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise EmergencyReserveError(
            "Emergency reserve directory identity could not be verified."
        ) from exc
    if is_link_boundary(path) or not stat.S_ISDIR(path_stat.st_mode) or not os.path.samestat(
        handle_stat,
        path_stat,
    ):
        raise EmergencyReserveError(
            "Emergency reserve directory changed during filesystem mutation."
        )


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
        self.path = self.reserve_root / _RESERVE_FILENAME

    def _prepare_root(self) -> None:
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
                durable_mkdir(self.reserve_root, parents=False, exist_ok=False)
            except FileExistsError as exc:
                # Another local process may have created the same durable directory
                # after our exists() check. Accept only the safe real directory that
                # now occupies the expected pathname; all redirecting boundaries fail.
                if is_link_boundary(self.reserve_root) or not self.reserve_root.is_dir():
                    raise EmergencyReserveError(
                        "Emergency reserve directory could not be created safely."
                    ) from exc
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve directory could not be created durably."
                ) from exc
        _assert_safe_parent(self.path)
        if is_link_boundary(self.path):
            raise EmergencyReserveError(
                "Emergency reserve file must not be a symlink, junction, or reparse point."
            )

    def _status_from_stat(
        self,
        *,
        required: int,
        stat_result: os.stat_result,
    ) -> EmergencyReserveStatus:
        try:
            return EmergencyReserveStatus(
                path=self.path,
                required_bytes=required,
                file_size_bytes=stat_result.st_size,
                allocated_bytes=_allocated_bytes_from_stat(stat_result),
            )
        except ValueError as exc:
            raise EmergencyReserveError(str(exc)) from exc

    def _wait_for_concurrent_creation(self, *, required: int) -> EmergencyReserveStatus:
        """Wait only while an incomplete reserve is demonstrably making progress.

        A second core/scheduler process can observe the O_EXCL winner after the file
        has been published but before its physical allocation write completes. That
        partial file is not corruption. Conversely, a stable wrong-sized file must
        still fail closed rather than becoming silently accepted.
        """
        deadline = time.monotonic() + _CONCURRENT_CREATION_TIMEOUT_SECONDS
        last_size: int | None = None
        last_progress = time.monotonic()

        while True:
            if is_link_boundary(self.path):
                raise EmergencyReserveError(
                    "Emergency reserve file became unsafe during concurrent creation."
                )
            try:
                current = self.path.stat(follow_symlinks=False)
            except FileNotFoundError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve disappeared during concurrent creation."
                ) from exc
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve metadata could not be read during concurrent creation."
                ) from exc

            if not stat.S_ISREG(current.st_mode):
                raise EmergencyReserveError(
                    "Emergency reserve path is not a regular file."
                )
            if current.st_size == required:
                return self.inspect(required_bytes=required)
            if current.st_size > required:
                return self.inspect(required_bytes=required)

            now = time.monotonic()
            if last_size is None or current.st_size > last_size:
                last_size = current.st_size
                last_progress = now
            elif now - last_progress >= _CONCURRENT_CREATION_STAGNANT_SECONDS:
                return self.inspect(required_bytes=required)

            if now >= deadline:
                return self.inspect(required_bytes=required)
            time.sleep(_CONCURRENT_CREATION_POLL_SECONDS)

    def _inspect_posix_with_root_fd(
        self,
        *,
        root_fd: int,
        required: int,
    ) -> EmergencyReserveStatus:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(_RESERVE_FILENAME, flags, dir_fd=root_fd)
        except FileNotFoundError as exc:
            raise EmergencyReserveError(
                "Emergency reserve file is missing or unsafe."
            ) from exc
        except OSError as exc:
            raise EmergencyReserveError(
                "Emergency reserve file could not be opened safely."
            ) from exc
        try:
            file_stat = os.fstat(descriptor)
            if not stat.S_ISREG(file_stat.st_mode):
                raise EmergencyReserveError(
                    "Emergency reserve path is not a regular file."
                )
            status = self._status_from_stat(required=required, stat_result=file_stat)
        finally:
            os.close(descriptor)
        _assert_posix_directory_current(self.reserve_root, root_fd)
        return status

    def _ensure_posix(
        self,
        *,
        required: int,
        chunk_bytes: int,
    ) -> EmergencyReserveStatus:
        root_fd = _open_posix_directory(self.reserve_root)
        created = False
        descriptor = -1
        try:
            _assert_posix_directory_current(self.reserve_root, root_fd)
            flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            try:
                descriptor = os.open(
                    _RESERVE_FILENAME,
                    flags,
                    0o600,
                    dir_fd=root_fd,
                )
                created = True
            except FileExistsError:
                try:
                    return self._inspect_posix_with_root_fd(
                        root_fd=root_fd,
                        required=required,
                    )
                except EmergencyReserveError as exc:
                    if "file size must exactly match required bytes" not in str(exc):
                        raise
                    return self._wait_for_concurrent_creation(required=required)
            except (NotImplementedError, TypeError) as exc:
                raise EmergencyReserveError(
                    "Identity-bound emergency reserve creation is unsupported."
                ) from exc
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve could not be opened for allocation."
                ) from exc

            os.fchmod(descriptor, 0o600)
            _write_allocated_bytes(
                descriptor,
                size_bytes=required,
                chunk_bytes=chunk_bytes,
            )
            os.fsync(descriptor)
            file_stat = os.fstat(descriptor)
            if not stat.S_ISREG(file_stat.st_mode):
                raise EmergencyReserveError(
                    "Emergency reserve allocation target is not a regular file."
                )
            status = self._status_from_stat(required=required, stat_result=file_stat)
            os.close(descriptor)
            descriptor = -1
            os.fsync(root_fd)
            _assert_posix_directory_current(self.reserve_root, root_fd)
            return status
        except BaseException as exc:
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                descriptor = -1
            if created:
                try:
                    os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)
                    os.fsync(root_fd)
                except OSError:
                    pass
            if isinstance(exc, EmergencyReserveError):
                raise
            if isinstance(exc, OSError):
                raise EmergencyReserveError(
                    "Emergency reserve could not be physically allocated."
                ) from exc
            raise
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(root_fd)

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
        self._prepare_root()

        if os.name == "posix":
            return self._ensure_posix(required=required, chunk_bytes=chunk_bytes)

        if self.path.exists():
            try:
                return self.inspect(required_bytes=required)
            except EmergencyReserveError as exc:
                if "file size must exactly match required bytes" not in str(exc):
                    raise
                return self._wait_for_concurrent_creation(required=required)

        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = -1
        created = False
        created_identity: os.stat_result | None = None
        try:
            try:
                descriptor = os.open(self.path, flags, 0o600)
                created = True
            except FileExistsError:
                # Losing O_EXCL means another process owns creation. Never enter
                # our cleanup path for that file; wait for the winner to finish.
                return self._wait_for_concurrent_creation(required=required)

            try:
                created_identity = os.fstat(descriptor)
                path_stat = self.path.stat(follow_symlinks=False)
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve file identity could not be verified."
                ) from exc
            if is_link_boundary(self.path) or not os.path.samestat(
                path_stat,
                created_identity,
            ):
                raise EmergencyReserveError(
                    "Emergency reserve pathname changed during creation."
                )
            _write_allocated_bytes(
                descriptor,
                size_bytes=required,
                chunk_bytes=chunk_bytes,
            )
            os.fsync(descriptor)
        except BaseException as exc:
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                descriptor = -1

            # Only remove the exact file identity created by this process. A lost
            # O_EXCL race or pathname replacement must never delete another
            # process's completed reserve or an attacker-controlled replacement.
            if created and created_identity is not None:
                try:
                    current = self.path.stat(follow_symlinks=False)
                    if not is_link_boundary(self.path) and os.path.samestat(
                        current,
                        created_identity,
                    ):
                        self.path.unlink()
                        fsync_directory(self.reserve_root)
                except OSError:
                    pass

            if isinstance(exc, EmergencyReserveError):
                raise
            if isinstance(exc, OSError):
                raise EmergencyReserveError(
                    "Emergency reserve could not be physically allocated."
                ) from exc
            raise
        finally:
            if descriptor >= 0:
                os.close(descriptor)

        fsync_directory(self.reserve_root)
        return self.inspect(required_bytes=required)

    def inspect(self, *, required_bytes: int) -> EmergencyReserveStatus:
        required = _positive_int(required_bytes, "Emergency reserve required_bytes")
        self._prepare_root()
        if os.name == "posix":
            root_fd = _open_posix_directory(self.reserve_root)
            try:
                return self._inspect_posix_with_root_fd(
                    root_fd=root_fd,
                    required=required,
                )
            finally:
                os.close(root_fd)

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
        self._prepare_root()
        if os.name == "posix":
            root_fd = _open_posix_directory(self.reserve_root)
            descriptor = -1
            try:
                _assert_posix_directory_current(self.reserve_root, root_fd)
                flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                try:
                    descriptor = os.open(_RESERVE_FILENAME, flags, dir_fd=root_fd)
                except FileNotFoundError:
                    return 0
                except (NotImplementedError, TypeError) as exc:
                    raise EmergencyReserveError(
                        "Identity-bound emergency reserve release is unsupported."
                    ) from exc
                except OSError as exc:
                    raise EmergencyReserveError(
                        "Emergency reserve file could not be opened safely for release."
                    ) from exc
                file_stat = os.fstat(descriptor)
                if not stat.S_ISREG(file_stat.st_mode):
                    raise EmergencyReserveError(
                        "Emergency reserve path is not a regular file."
                    )
                size = file_stat.st_size
                os.close(descriptor)
                descriptor = -1
                _assert_posix_directory_current(self.reserve_root, root_fd)
                os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)
                os.fsync(root_fd)
                _assert_posix_directory_current(self.reserve_root, root_fd)
                return size
            except OSError as exc:
                raise EmergencyReserveError(
                    "Emergency reserve could not be released durably."
                ) from exc
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
                os.close(root_fd)

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


VolumeSizeProvider = Callable[[Path], int]


def _default_volume_size(path: Path) -> int:
    try:
        return int(shutil.disk_usage(path).total)
    except OSError as exc:
        raise EmergencyReserveError(
            "Emergency reserve volume size could not be determined."
        ) from exc


class EmergencyReserveService:
    """Lifecycle service that provisions the Beta-03 reserve before DB startup.

    The service never removes the reserve during normal shutdown. Recovery and
    disk-pressure control own explicit release semantics.
    """

    name = "emergency-reserve"

    def __init__(
        self,
        state_root: Path,
        *,
        volume_size_provider: VolumeSizeProvider | None = None,
        required_bytes_override: int | None = None,
        write_chunk_bytes: int = _DEFAULT_WRITE_CHUNK_BYTES,
    ) -> None:
        self.store = EmergencyReserveStore(state_root)
        self._volume_size_provider = volume_size_provider or _default_volume_size
        self._required_bytes_override = (
            None
            if required_bytes_override is None
            else _positive_int(
                required_bytes_override,
                "Emergency reserve required_bytes_override",
            )
        )
        self._write_chunk_bytes = _positive_int(
            write_chunk_bytes,
            "Emergency reserve write_chunk_bytes",
        )
        self.status: EmergencyReserveStatus | None = None

    def required_bytes(self) -> int:
        if self._required_bytes_override is not None:
            return self._required_bytes_override
        volume_size = self._volume_size_provider(self.store.state_root)
        return emergency_reserve_size_bytes(volume_size)

    def start(self) -> None:
        required = self.required_bytes()
        self.status = self.store.ensure(
            required_bytes=required,
            write_chunk_bytes=self._write_chunk_bytes,
        )

    def stop(self) -> None:
        return
