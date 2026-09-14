from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

import pytest

from athena.observability.jsonl import configure_jsonl_logging
from athena.observability.logging import configure_logging


def _owned_jsonl_handlers(logger: logging.Logger) -> list[logging.Handler]:
    return [
        handler
        for handler in logger.handlers
        if getattr(handler, "_athena_jsonl_handler", False)
    ]


def _owned_console_handlers(root: logging.Logger) -> list[logging.Handler]:
    return [
        handler
        for handler in root.handlers
        if getattr(handler, "_athena_console_handler", False)
    ]


def _remove_owned_jsonl_handlers() -> None:
    for logger in (logging.getLogger("athena"), logging.getLogger()):
        for handler in list(_owned_jsonl_handlers(logger)):
            logger.removeHandler(handler)
            handler.close()


def _remove_owned_console_handlers(root: logging.Logger) -> None:
    for handler in list(_owned_console_handlers(root)):
        root.removeHandler(handler)
        handler.close()


def test_configure_jsonl_logging_is_idempotent_and_uses_shared_redaction(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena.jsonl"

    try:
        _remove_owned_jsonl_handlers()
        configure_jsonl_logging(log_path, level=logging.INFO)
        configure_jsonl_logging(log_path, level="INFO")

        handlers = _owned_jsonl_handlers(athena)
        assert len(handlers) == 1
        assert not _owned_jsonl_handlers(root)

        logging.getLogger("athena.test").info(
            "persist diagnostic",
            extra={
                "event": "test.jsonl",
                "api_key": "never-persist-this",
                "prompt": "private semantic content",
            },
        )
        handlers[0].flush()

        payload = json.loads(log_path.read_text(encoding="utf-8"))
        assert payload["event"] == "test.jsonl"
        assert payload["message"] == "persist diagnostic"
        assert payload["api_key"] == "[REDACTED]"
        assert payload["prompt"] == "[REDACTED_CONTENT]"
        assert "never-persist-this" not in log_path.read_text(encoding="utf-8")
        assert "private semantic content" not in log_path.read_text(encoding="utf-8")
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_logging_rotates_with_bounded_retention(tmp_path: Path) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena.jsonl"

    try:
        _remove_owned_jsonl_handlers()
        configure_jsonl_logging(
            log_path,
            level=logging.INFO,
            max_bytes=256,
            backup_count=2,
        )
        logger = logging.getLogger("athena.rotation")
        for index in range(12):
            logger.info(
                "rotation event %s",
                index,
                extra={
                    "event": "test.rotation",
                    "safe_detail": "x" * 96,
                    "secret": "must-not-survive-rotation",
                },
            )

        handlers = _owned_jsonl_handlers(athena)
        assert len(handlers) == 1
        handlers[0].flush()

        retained = sorted(tmp_path.glob("athena.jsonl*"))
        assert len(retained) == 3
        assert log_path in retained

        for retained_path in retained:
            text = retained_path.read_text(encoding="utf-8")
            assert "must-not-survive-rotation" not in text
            lines = [line for line in text.splitlines() if line]
            assert lines
            for line in lines:
                payload = json.loads(line)
                assert payload["event"] == "test.rotation"
                assert payload["secret"] == "[REDACTED]"
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_logging_replaces_owned_handler_when_policy_changes(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    first_path = tmp_path / "first.jsonl"
    second_path = tmp_path / "second.jsonl"

    try:
        _remove_owned_jsonl_handlers()
        configure_jsonl_logging(first_path, max_bytes=1024, backup_count=2)
        first_handler = _owned_jsonl_handlers(athena)[0]

        configure_jsonl_logging(second_path, max_bytes=2048, backup_count=3)
        handlers = _owned_jsonl_handlers(athena)

        assert len(handlers) == 1
        assert handlers[0] is not first_handler
        assert isinstance(handlers[0], RotatingFileHandler)
        assert Path(handlers[0].baseFilename) == second_path
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_debug_survives_later_console_info_reconfiguration(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena.jsonl"

    try:
        _remove_owned_jsonl_handlers()
        _remove_owned_console_handlers(root)

        configure_jsonl_logging(log_path, level=logging.DEBUG)
        configure_logging(logging.INFO)

        logging.getLogger("athena.order").debug(
            "file-only debug",
            extra={"event": "test.order.jsonl_more_verbose"},
        )
        handlers = _owned_jsonl_handlers(athena)
        assert len(handlers) == 1
        handlers[0].flush()

        payload = json.loads(log_path.read_text(encoding="utf-8"))
        assert payload["event"] == "test.order.jsonl_more_verbose"
        assert root.level == logging.INFO
        assert athena.level == 1
        assert _owned_console_handlers(root)[0].level == logging.INFO
    finally:
        _remove_owned_jsonl_handlers()
        _remove_owned_console_handlers(root)
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_handler_keeps_own_threshold_when_console_is_more_verbose(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena.jsonl"

    try:
        _remove_owned_jsonl_handlers()
        _remove_owned_console_handlers(root)

        configure_logging(logging.DEBUG)
        configure_jsonl_logging(log_path, level=logging.INFO)

        logger = logging.getLogger("athena.order")
        logger.debug(
            "console-only debug",
            extra={"event": "test.order.console_more_verbose.debug"},
        )
        logger.info(
            "shared info",
            extra={"event": "test.order.console_more_verbose.info"},
        )
        handlers = _owned_jsonl_handlers(athena)
        assert len(handlers) == 1
        handlers[0].flush()

        text = log_path.read_text(encoding="utf-8")
        assert "test.order.console_more_verbose.debug" not in text
        assert "test.order.console_more_verbose.info" in text
        assert root.level == logging.DEBUG
        assert athena.level == 1
        assert handlers[0].level == logging.INFO
    finally:
        _remove_owned_jsonl_handlers()
        _remove_owned_console_handlers(root)
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "10"])
def test_jsonl_logging_rejects_invalid_max_bytes(
    tmp_path: Path,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="max_bytes"):
        configure_jsonl_logging(
            tmp_path / "athena.jsonl",
            max_bytes=cast(int, value),
        )


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "2"])
def test_jsonl_logging_rejects_invalid_backup_count(
    tmp_path: Path,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="backup_count"):
        configure_jsonl_logging(
            tmp_path / "athena.jsonl",
            backup_count=cast(int, value),
        )


def test_jsonl_logging_rejects_missing_parent_and_non_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="parent directory"):
        configure_jsonl_logging(tmp_path / "missing" / "athena.jsonl")

    with pytest.raises(TypeError, match="pathlib.Path"):
        configure_jsonl_logging(cast(Path, str(tmp_path / "athena.jsonl")))
