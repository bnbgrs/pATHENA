from __future__ import annotations

import argparse
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.desktop.claims_cli import _run
from athena.knowledge.models import ClaimKind, EpistemicStatus


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def test_desktop_claims_list_show_evidence_and_history_survive_restart(
    tmp_path: Path,
    capsys,
) -> None:
    root = tmp_path / "runtime"
    first = _app(root)
    try:
        chat_id = first.chat.create_chat()
        first_message = first.chat.add_user_message(
            chat_id=chat_id,
            content="Claim A before revision.",
        )
        second_message = first.chat.add_user_message(
            chat_id=chat_id,
            content="Claim B contradicts Claim A.",
        )
        first_claim = first.claims.promote_chat_message(
            chat_id=chat_id,
            sequence_no=first_message.sequence_no,
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
        )
        second_claim = first.claims.promote_chat_message(
            chat_id=chat_id,
            sequence_no=second_message.sequence_no,
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
        )
        revised = first.claims.revise(
            claim_id=first_claim.claim_id,
            statement="Claim A after revision.",
            epistemic_status=EpistemicStatus.SUPPORTED,
        )
        assert revised.revision_no == 2
        first.claims.mark_contradiction(
            left_claim_id=first_claim.claim_id,
            right_claim_id=second_claim.claim_id,
        )
        first_claim_id = first_claim.claim_id
        second_claim_id = second_claim.claim_id
    finally:
        first.stop()

    second = _app(root)
    try:
        assert _run(second, argparse.Namespace(command="list", limit=20)) == 0
        listing = capsys.readouterr().out
        assert str(first_claim_id) in listing
        assert "\t2\tfactual_assertion\tsupported\t" in listing
        assert "Claim A after revision." in listing

        assert _run(
            second,
            argparse.Namespace(command="show", claim_id=first_claim_id),
        ) == 0
        shown = capsys.readouterr().out
        assert f"CLAIM {first_claim_id}" in shown
        assert "REVISION 2 " in shown
        assert "STATUS supported" in shown
        assert "Claim A after revision." in shown
        assert "PROVENANCE_INPUTS" in shown
        assert "EVIDENCE_REF role=originates" in shown
        assert "EVIDENCE_REF role=contradicts" in shown
        assert f"entity={second_claim_id}" in shown

        assert _run(
            second,
            argparse.Namespace(command="history", claim_id=first_claim_id),
        ) == 0
        history = capsys.readouterr().out
        assert "HISTORY 2" in history
        assert "REVISION 1 " in history
        assert "REVISION 2 " in history
        assert "Claim A before revision." in history
        assert "Claim A after revision." in history
    finally:
        second.stop()
