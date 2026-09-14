"""Persistent privacy-preserving JSONL logging for ATHENA diagnostics."""

from __future__ import annotations

import logging
import os
import stat
from io import TextIOWrapper
from logging.handlers import RotatingFileHandler
from pathlib import Path

from athena.observability.logging import JsonFormatter

_FILE_HANDLER_MARKER = "_athena_jsonl_handler"
DEFAULT_JSONL_MAX_BYTES = 8 * 1024 * 1024
DEFAULT_JSONL_BACKUP_COUNT = 5


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction is not None and is_junction())


def _validate_open_file(path: Path, file_descriptor: int) -> None:
    """Prove that an opened log descriptor still names one regular path."""

    parent = path.parent
    try:
        parent_stat = os.lstat(parent)
        path_stat = os.lstat(path)
        opened_stat = os.fstat(file_descriptor)
    except OSError as exc:
        raise ValueError("ATHENA JSONL log identity changed during open.") from exc

    if not stat.S_ISDIR(parent_stat.st_mode) or _is_link_or_junction(parent):
        raise ValueError("log_path parent directory must not be a symbolic link or junction.")
    if (
        not stat.S_ISREG(path_stat.st_mode)
        or _is_link_or_junction(path)
        or not stat.S_ISREG(opened_stat.st_mode)
    ):
        raise ValueError("log_path must identify one regular non-link file.")
    if not os.path.samestat(opened_stat, path_stat):
        raise ValueError("ATHENA JSONL log identity changed during open.")


class _SecureRotatingFileHandler(RotatingFileHandler):
    """Rotating handler that revalidates path identity at every real open."""

    def _open(self) -> TextIOWrapper:
        def opener(filename: str, flags: int) -> int:
            secure_flags = flags
            no_follow = getattr(os, "O_NOFOLLOW", 0)
            close_on_exec = getattr(os, "O_CLOEXEC", 0)
            secure_flags |= no_follow | close_on_exec

            descriptor = os.open(filename, secure_flags, 0o600)
            try:
                _validate_open_file(Path(filename), descriptor)
            except Exception:
                os.close(descriptor)
                raise
            return descriptor

        return self._builtin_open(
            self.baseFilename,
            self.mode,
            encoding=self.encoding,
            errors=self.errors,
            opener=opener,
        )


def _validated_log_level(level: object) -> int:
    if isinstance(level, bool):
        raise ValueError("ATHENA JSONL logging level must not be a boolean.")
    if isinstance(level, str):
        normalized = level.strip().upper()
        if not normalized:
            raise ValueError("ATHENA JSONL logging level must not be empty.")
        numeric = logging.getLevelNamesMapping().get(normalized)
        if not isinstance(numeric, int):
            raise ValueError(f"Unknown ATHENA JSONL logging level {level!r}.")
        return numeric
    if isinstance(level, int):
        if level < 0:
            raise ValueError("ATHENA JSONL logging level must be non-negative.")
        return level
    raise ValueError("ATHENA JSONL logging level must be an integer or level name.")


def _validated_positive_int(value: object, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value


def _validated_log_path(log_path: object) -> Path:
    if not isinstance(log_path, Path):
        raise TypeError("log_path must be a pathlib.Path.")
    if _is_link_or_junction(log_path):
        raise ValueError("log_path must not be a symbolic link or junction.")
    if log_path.exists() and not log_path.is_file():
        raise ValueError("log_path must identify a regular file.")

    parent = log_path.parent
    if not parent.exists() or not parent.is_dir():
        raise ValueError("log_path parent directory must already exist.")
    if _is_link_or_junction(parent):
        raise ValueError("log_path parent directory must not be a symbolic link or junction.")
    return log_path.absolute()


def _rotated_backup_index(path: Path, candidate: Path) -> int | None:
    prefix = f"{path.name}."
    if not candidate.name.startswith(prefix):
        return None
    suffix = candidate.name[len(prefix) :]
    if not suffix.isascii() or not suffix.isdigit():
        return None
    index = int(suffix)
    return index if index >= 1 else None


def _prune_stale_rotated_files(path: Path, backup_count: int) -> None:
    """Remove numeric rotated files outside the configured retention window."""
    for candidate in path.parent.iterdir():
        index = _rotated_backup_index(path, candidate)
        if index is None or index <= backup_count:
            continue

        try:
            mode = candidate.lstat().st_mode
        except FileNotFoundError:
            continue
        if not (stat.S_ISREG(mode) or stat.S_ISLNK(mode)):
            raise ValueError(
                "stale rotated log path must be a regular file or symbolic link."
            )
        try:
            candidate.unlink()
        except FileNotFoundError:
            continue


def configure_jsonl_logging(
    log_path: Path,
    *,
    level: int | str = logging.INFO,
    max_bytes: int = DEFAULT_JSONL_MAX_BYTES,
    backup_count: int = DEFAULT_JSONL_BACKUP_COUNT,
) -> None:
    """Configure one ATHENA-owned rotating JSONL file handler.

    The caller owns the directory lifecycle and containment policy. This function
    refuses missing directories and link/junction targets, emits one JSON object
    per line through the shared privacy-preserving formatter, and retains at most
    ``backup_count`` rotated files plus the active file. Every delayed first open
    and rollover reopen revalidates the actual file descriptor against the path,
    so a link substitution after configuration fails closed before bytes are
    written through that substituted path.

    Repeated calls with the same configuration reuse the owned handler instead
    of duplicating persisted events. A changed path or rotation policy replaces
    the previous ATHENA-owned JSONL handler deterministically. Numeric backups
    outside a reduced retention window are pruned before the new handler opens.
    """
    path = _validated_log_path(log_path)
    numeric_level = _validated_log_level(level)
    validated_max_bytes = _validated_positive_int(max_bytes, "max_bytes")
    validated_backup_count = _validated_positive_int(backup_count, "backup_count")

    root_logger = logging.getLogger()
    owned_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _FILE_HANDLER_MARKER, False)
    ]

    reusable: RotatingFileHandler | None = None
    for handler in owned_handlers:
        if (
            reusable is None
            and isinstance(handler, _SecureRotatingFileHandler)
            and Path(handler.baseFilename) == path
            and handler.maxBytes == validated_max_bytes
            and handler.backupCount == validated_backup_count
        ):
            reusable = handler
            continue
        root_logger.removeHandler(handler)
        handler.close()

    _prune_stale_rotated_files(path, validated_backup_count)

    if root_logger.level != logging.NOTSET and root_logger.level > numeric_level:
        root_logger.setLevel(numeric_level)

    if reusable is not None:
        reusable.setLevel(numeric_level)
        reusable.setFormatter(JsonFormatter())
        return

    handler = _SecureRotatingFileHandler(
        path,
        maxBytes=validated_max_bytes,
        backupCount=validated_backup_count,
        encoding="utf-8",
        delay=True,
    )
    setattr(handler, _FILE_HANDLER_MARKER, True)
    handler.setLevel(numeric_level)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
