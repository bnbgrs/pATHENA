"""Bounded persistent JSON Lines logging for ATHENA.

The privacy/redaction contract remains owned by :class:`JsonFormatter`.  This
module only provides the local persistence boundary required by Beta chapter
24: line-oriented JSON, size/time rotation and bounded retention.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from athena.observability.logging import JsonFormatter

_LOG_FILE_NAME = "athena.jsonl"
_HANDLER_MARKER = "_athena_persistent_jsonl_handler"


@dataclass(frozen=True, slots=True)
class JsonlRotationPolicy:
    """Explicit bounded-retention policy for technical JSONL logs."""

    max_bytes: int
    max_age_seconds: int
    retained_files: int

    def __post_init__(self) -> None:
        _require_positive_int(self.max_bytes, "max_bytes")
        _require_positive_int(self.max_age_seconds, "max_age_seconds")
        _require_positive_int(self.retained_files, "retained_files")


def _require_positive_int(value: object, field_name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    return value


def _validated_level(level: object) -> int:
    if type(level) is not int or level < 0:
        raise ValueError("Persistent log level must be a non-negative integer.")
    return level


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SizeAndTimeRotatingJsonlHandler(RotatingFileHandler):
    """Rotate an active JSONL log on size or configured UTC time buckets.

    Time rotation is evaluated on the next emitted record, matching standard
    logging-handler behavior during idle periods. Numeric ``.1``/``.2`` backup
    files are managed by :class:`RotatingFileHandler`, so repeated size
    rollovers inside one time bucket cannot overwrite each other.
    """

    def __init__(
        self,
        filename: Path,
        *,
        policy: JsonlRotationPolicy,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(filename, Path):
            raise TypeError("filename must be a pathlib.Path.")
        if not isinstance(policy, JsonlRotationPolicy):
            raise TypeError("policy must be JsonlRotationPolicy.")
        self.policy = policy
        self._clock = clock or _utc_now
        super().__init__(
            filename,
            mode="a",
            maxBytes=policy.max_bytes,
            backupCount=policy.retained_files,
            encoding="utf-8",
            delay=True,
        )
        self._active_time_bucket = self._initial_time_bucket()

    def _clock_timestamp(self) -> float:
        moment = self._clock()
        if not isinstance(moment, datetime):
            raise TypeError("Persistent logging clock must return datetime.")
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("Persistent logging clock must be timezone-aware.")
        return moment.astimezone(timezone.utc).timestamp()

    def _bucket_for_timestamp(self, timestamp: float) -> int:
        return int(timestamp // self.policy.max_age_seconds)

    def _initial_time_bucket(self) -> int:
        log_path = Path(self.baseFilename)
        try:
            stat = log_path.stat()
        except FileNotFoundError:
            return self._bucket_for_timestamp(self._clock_timestamp())
        if stat.st_size == 0:
            return self._bucket_for_timestamp(self._clock_timestamp())
        return self._bucket_for_timestamp(stat.st_mtime)

    def shouldRollover(self, record: logging.LogRecord) -> bool:  # noqa: N802
        current_bucket = self._bucket_for_timestamp(self._clock_timestamp())
        if current_bucket != self._active_time_bucket:
            return True
        return bool(super().shouldRollover(record))

    def doRollover(self) -> None:  # noqa: N802
        super().doRollover()
        self._active_time_bucket = self._bucket_for_timestamp(
            self._clock_timestamp()
        )


def configure_persistent_jsonl_logging(
    *,
    log_root: Path,
    policy: JsonlRotationPolicy,
    level: int = logging.INFO,
) -> Path:
    """Install exactly one ATHENA-owned persistent JSONL handler.

    ``log_root`` is expected to come from the already validated local
    :class:`~athena.storage.paths.RuntimePaths` boundary.  This function does
    not create or relocate storage roots and therefore cannot silently turn
    technical logging into a second arbitrary archive.
    """
    if not isinstance(log_root, Path):
        raise TypeError("log_root must be a pathlib.Path.")
    if not log_root.is_dir():
        raise ValueError("log_root must already exist as a directory.")
    if not isinstance(policy, JsonlRotationPolicy):
        raise TypeError("policy must be JsonlRotationPolicy.")
    numeric_level = _validated_level(level)

    log_path = (log_root / _LOG_FILE_NAME).resolve()
    root_logger = logging.getLogger()
    if root_logger.level != logging.NOTSET:
        root_logger.setLevel(min(root_logger.level, numeric_level))

    owned_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _HANDLER_MARKER, False)
    ]
    matching_handler: SizeAndTimeRotatingJsonlHandler | None = None
    for handler in owned_handlers:
        if (
            matching_handler is None
            and isinstance(handler, SizeAndTimeRotatingJsonlHandler)
            and Path(handler.baseFilename) == log_path
            and handler.policy == policy
        ):
            matching_handler = handler
            continue
        root_logger.removeHandler(handler)
        handler.close()

    formatter = JsonFormatter()
    if matching_handler is not None:
        matching_handler.setLevel(numeric_level)
        matching_handler.setFormatter(formatter)
        return log_path

    handler = SizeAndTimeRotatingJsonlHandler(log_path, policy=policy)
    setattr(handler, _HANDLER_MARKER, True)
    handler.setLevel(numeric_level)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    return log_path
