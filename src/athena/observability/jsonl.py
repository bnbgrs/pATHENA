"""Persistent privacy-preserving JSONL logging for ATHENA diagnostics."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from athena.observability.logging import JsonFormatter

_FILE_HANDLER_MARKER = "_athena_jsonl_handler"
DEFAULT_JSONL_MAX_BYTES = 8 * 1024 * 1024
DEFAULT_JSONL_BACKUP_COUNT = 5


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
    if log_path.is_symlink():
        raise ValueError("log_path must not be a symbolic link.")
    if log_path.exists() and not log_path.is_file():
        raise ValueError("log_path must identify a regular file.")

    parent = log_path.parent
    if not parent.exists() or not parent.is_dir():
        raise ValueError("log_path parent directory must already exist.")
    if parent.is_symlink():
        raise ValueError("log_path parent directory must not be a symbolic link.")
    return log_path.absolute()


def configure_jsonl_logging(
    log_path: Path,
    *,
    level: int | str = logging.INFO,
    max_bytes: int = DEFAULT_JSONL_MAX_BYTES,
    backup_count: int = DEFAULT_JSONL_BACKUP_COUNT,
) -> None:
    """Configure one ATHENA-owned rotating JSONL file handler.

    The caller owns the directory lifecycle and containment policy. This function
    refuses missing directories and direct symbolic-link targets, emits one JSON
    object per line through the shared privacy-preserving formatter, and retains
    at most ``backup_count`` rotated files plus the active file.

    Repeated calls with the same configuration reuse the owned handler instead
    of duplicating persisted events. A changed path or rotation policy replaces
    the previous ATHENA-owned JSONL handler deterministically.
    """
    path = _validated_log_path(log_path)
    numeric_level = _validated_log_level(level)
    validated_max_bytes = _validated_positive_int(max_bytes, "max_bytes")
    validated_backup_count = _validated_positive_int(backup_count, "backup_count")

    root_logger = logging.getLogger()
    if root_logger.level != logging.NOTSET and root_logger.level > numeric_level:
        root_logger.setLevel(numeric_level)

    owned_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _FILE_HANDLER_MARKER, False)
    ]

    reusable: RotatingFileHandler | None = None
    for handler in owned_handlers:
        if (
            reusable is None
            and isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename) == path
            and handler.maxBytes == validated_max_bytes
            and handler.backupCount == validated_backup_count
        ):
            reusable = handler
            continue
        root_logger.removeHandler(handler)
        handler.close()

    if reusable is not None:
        reusable.setLevel(numeric_level)
        reusable.setFormatter(JsonFormatter())
        return

    handler = RotatingFileHandler(
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
