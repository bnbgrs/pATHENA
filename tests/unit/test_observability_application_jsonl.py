from __future__ import annotations

import json
import logging
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication


def _owned_jsonl_handlers() -> list[logging.Handler]:
    handlers: list[logging.Handler] = []
    for logger in (logging.getLogger("athena"), logging.getLogger()):
        handlers.extend(
            handler
            for handler in logger.handlers
            if getattr(handler, "_athena_jsonl_handler", False)
        )
    return handlers


def test_application_enables_persistent_jsonl_after_storage_start(tmp_path: Path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "runtime",
        )
    )
    log_path = app.paths.log_root / "athena.jsonl"

    assert not log_path.exists()

    app.start()
    try:
        assert app.paths.log_root.is_dir()
        assert len(_owned_jsonl_handlers()) == 1

        logging.getLogger("athena.integration").info(
            "application jsonl marker",
            extra={"event": "test.application_jsonl"},
        )
    finally:
        app.stop()

    payloads = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    events = {payload.get("event") for payload in payloads}

    assert "core.logging_persistent_ready" in events
    assert "test.application_jsonl" in events
    assert "core.running" in events
    assert "core.stopped" in events
    assert _owned_jsonl_handlers() == []


def test_application_restart_reopens_one_owned_jsonl_handler(tmp_path: Path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "runtime",
        )
    )

    app.start()
    app.stop()
    assert _owned_jsonl_handlers() == []

    app.start()
    try:
        assert len(_owned_jsonl_handlers()) == 1
    finally:
        app.stop()

    assert _owned_jsonl_handlers() == []
