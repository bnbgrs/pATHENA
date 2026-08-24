"""Structured console logging for ATHENA."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

_HANDLER_MARKER = "_athena_console_handler"


class JsonFormatter(logging.Formatter):
    """Small deterministic JSON formatter for Core diagnostic events."""

    _standard_fields = frozenset(
        {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if (
                key not in self._standard_fields
                and not key.startswith("_")
                and key not in payload
            ):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )


def _validated_log_level(level: object) -> int:
    if isinstance(level, bool):
        raise ValueError("ATHENA logging level must not be a boolean.")
    if isinstance(level, str):
        normalized = level.strip().upper()
        if not normalized:
            raise ValueError("ATHENA logging level must not be empty.")
        numeric = logging.getLevelNamesMapping().get(normalized)
        if not isinstance(numeric, int):
            raise ValueError(f"Unknown ATHENA logging level {level!r}.")
        return numeric
    if isinstance(level, int):
        if level < 0:
            raise ValueError("ATHENA logging level must be non-negative.")
        return level
    raise ValueError("ATHENA logging level must be an integer or level name.")


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configure exactly one ATHENA-owned console handler.

    Repeated calls update the handler and root log level without creating
    duplicate log lines.
    """
    numeric_level = _validated_log_level(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    athena_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _HANDLER_MARKER, False)
    ]

    if athena_handlers:
        handler = athena_handlers[0]
        handler.setLevel(numeric_level)
        handler.setFormatter(JsonFormatter())

        for duplicate in athena_handlers[1:]:
            root_logger.removeHandler(duplicate)
            duplicate.close()
        return

    handler = logging.StreamHandler()
    setattr(handler, _HANDLER_MARKER, True)
    handler.setLevel(numeric_level)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
