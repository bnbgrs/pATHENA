from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication


def test_application_binds_chat_to_chat_knowledge_extraction(tmp_path: Path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path.absolute()),
    )

    assert app.extraction.chat is app.chat
    assert app.extraction.chat_generation is app.chat_generation
