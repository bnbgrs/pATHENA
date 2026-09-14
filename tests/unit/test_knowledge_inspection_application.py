from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication


def test_application_attaches_canonical_knowledge_inspection(tmp_path: Path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path.absolute()),
    )

    assert app.api._knowledge_inspection is app.knowledge_inspection_api
    assert app.knowledge_inspection_api._inspection._claims is app.claims
    assert app.knowledge_inspection_api._inspection._reviews is app.reviews

    actor_provider = app.knowledge_inspection_api._actor_id_provider
    assert actor_provider.__self__ is app.chat
    assert actor_provider.__func__ is app.chat.ensure_local_user.__func__

    features = set(app.api.capabilities().features)
    assert "knowledge.claim.inspect" in features
    assert "knowledge.review.contradiction" in features
