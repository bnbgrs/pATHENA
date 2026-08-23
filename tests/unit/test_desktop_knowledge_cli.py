from __future__ import annotations

import argparse
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.desktop.knowledge_cli import _run
from athena.knowledge.models import EpistemicStatus, KnowledgeKind


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def test_desktop_knowledge_list_show_and_history_survive_restart(
    tmp_path: Path,
    capsys,
) -> None:
    root = tmp_path / "runtime"
    first = _app(root)
    try:
        chat_id = first.chat.create_chat()
        message = first.chat.add_user_message(
            chat_id=chat_id,
            content="Persistent desktop knowledge marker.",
        )
        created = first.knowledge.promote_chat_message(
            chat_id=chat_id,
            sequence_no=message.sequence_no,
            knowledge_kind=KnowledgeKind.IDEA,
            title="Durable browser entry",
        )
        revised = first.knowledge.revise(
            knowledge_id=created.knowledge_id,
            body="Persistent desktop knowledge marker, revised.",
            epistemic_status=EpistemicStatus.SUPPORTED,
        )
        assert revised.revision_no == 2
        knowledge_id = created.knowledge_id
    finally:
        first.stop()

    second = _app(root)
    try:
        assert _run(second, argparse.Namespace(command="list", limit=20)) == 0
        listing = capsys.readouterr().out
        assert str(knowledge_id) in listing
        assert "\t2\tidea\tsupported\t" in listing
        assert "Durable browser entry" in listing

        assert _run(
            second,
            argparse.Namespace(command="show", knowledge_id=knowledge_id),
        ) == 0
        shown = capsys.readouterr().out
        assert f"KNOWLEDGE {knowledge_id}" in shown
        assert "REVISION 2 " in shown
        assert "STATUS supported" in shown
        assert "Persistent desktop knowledge marker, revised." in shown
        assert "PROVENANCE_INPUTS" in shown

        assert _run(
            second,
            argparse.Namespace(command="history", knowledge_id=knowledge_id),
        ) == 0
        history = capsys.readouterr().out
        assert "HISTORY 2" in history
        assert "REVISION 1 " in history
        assert "REVISION 2 " in history
        assert "Persistent desktop knowledge marker." in history
        assert "Persistent desktop knowledge marker, revised." in history
    finally:
        second.stop()
