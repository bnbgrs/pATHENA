from __future__ import annotations

import uuid
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from scripts.render_pathena_ui_snapshot_sequential import (
    _REFERENCE_CHAT_MESSAGES,
    _seed_reference_chat,
)


def test_visual_chat_fixture_is_idempotent_and_repository_backed(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "isolated-visual-runtime"

    first_id = _seed_reference_chat(runtime_root)
    second_id = _seed_reference_chat(runtime_root)

    assert second_id == first_id

    core = AthenaApplication(
        settings=AthenaSettings(local_root=runtime_root)
    )
    core.start(run_startup_maintenance=False)
    try:
        thread = core.chat.load_chat(uuid.UUID(first_id))
        actual = tuple(
            (
                message.message_type.value,
                message.content or "",
            )
            for message in thread.messages
        )
        assert actual == _REFERENCE_CHAT_MESSAGES
        assert len(thread.messages) == len(_REFERENCE_CHAT_MESSAGES)
    finally:
        core.stop()
