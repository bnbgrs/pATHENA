from __future__ import annotations

import logging
from pathlib import Path

import pytest

from athena.observability.jsonl import configure_jsonl_logging


def _owned_jsonl_handlers(logger: logging.Logger) -> list[logging.Handler]:
    return [
        handler
        for handler in logger.handlers
        if getattr(handler, "_athena_jsonl_handler", False)
    ]


def _remove_owned_jsonl_handlers() -> None:
    for logger in (logging.getLogger("athena"), logging.getLogger()):
        for handler in list(_owned_jsonl_handlers(logger)):
            logger.removeHandler(handler)
            handler.close()


def test_jsonl_logging_prunes_backups_outside_reduced_retention(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena.jsonl"
    unrelated = tmp_path / "athena.jsonl.notes"

    try:
        _remove_owned_jsonl_handlers()
        for index in range(1, 6):
            (tmp_path / f"athena.jsonl.{index}").write_text(
                f"backup-{index}", encoding="utf-8"
            )
        unrelated.write_text("keep", encoding="utf-8")

        configure_jsonl_logging(log_path, backup_count=2)

        assert (tmp_path / "athena.jsonl.1").exists()
        assert (tmp_path / "athena.jsonl.2").exists()
        assert not (tmp_path / "athena.jsonl.3").exists()
        assert not (tmp_path / "athena.jsonl.4").exists()
        assert not (tmp_path / "athena.jsonl.5").exists()
        assert unrelated.read_text(encoding="utf-8") == "keep"
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_retention_matches_metacharacters_as_literal_filename(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    log_path = tmp_path / "athena[1].jsonl"
    own_stale_backup = tmp_path / "athena[1].jsonl.3"
    unrelated_pattern_match = tmp_path / "athena1.jsonl.9"

    try:
        _remove_owned_jsonl_handlers()
        own_stale_backup.write_text("stale", encoding="utf-8")
        unrelated_pattern_match.write_text("foreign", encoding="utf-8")

        configure_jsonl_logging(log_path, backup_count=2)

        assert not own_stale_backup.exists()
        assert unrelated_pattern_match.read_text(encoding="utf-8") == "foreign"
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)


def test_jsonl_logging_fails_closed_on_non_file_stale_backup(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    athena = logging.getLogger("athena")
    original_root_level = root.level
    original_athena_level = athena.level
    stale_directory = tmp_path / "athena.jsonl.3"
    stale_directory.mkdir()

    try:
        _remove_owned_jsonl_handlers()
        with pytest.raises(ValueError, match="stale rotated log path"):
            configure_jsonl_logging(tmp_path / "athena.jsonl", backup_count=2)
        assert not _owned_jsonl_handlers(athena)
        assert not _owned_jsonl_handlers(root)
        assert stale_directory.is_dir()
    finally:
        _remove_owned_jsonl_handlers()
        root.setLevel(original_root_level)
        athena.setLevel(original_athena_level)
