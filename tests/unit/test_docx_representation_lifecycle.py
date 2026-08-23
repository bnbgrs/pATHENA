from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any, cast

import pytest

from athena.chat.service import ChatService
from athena.model.provenance import ModelRunRepository
from athena.source.blob_store import BlobStore
from athena.source.docx_representation_service import SourceDocxRepresentationService
from athena.source.docx_representation_store import DocxNativeTextRepresentationStore
from athena.source.repository import SourceRepository
from athena.source.representation_repository import SourceRepresentationRepository


class _Sources:
    def __init__(self) -> None:
        self.source_id = uuid.uuid4()
        self.blob_id = uuid.uuid4()

    def get(self, source_id: uuid.UUID) -> tuple[Any, Any]:
        assert source_id == self.source_id
        return (
            SimpleNamespace(
                source_id=self.source_id,
                content_sha256=b"x" * 32,
                mime_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                original_name="source.docx",
            ),
            SimpleNamespace(
                blob_id=self.blob_id,
                byte_length=10,
                storage_area="spool",
                storage_locator="source.docx",
                integrity_sha256=b"y" * 32,
            ),
        )


class _Chat:
    def ensure_local_user(self) -> uuid.UUID:
        return uuid.uuid4()


class _Runs:
    def __init__(self) -> None:
        self.run_id = uuid.uuid4()
        self.finished: list[tuple[uuid.UUID, str]] = []

    def start_run(self, **kwargs: object) -> Any:
        return SimpleNamespace(processing_run_id=self.run_id)

    def load_run(self, processing_run_id: uuid.UUID) -> Any:
        assert processing_run_id == self.run_id
        return SimpleNamespace(status="running")

    def finish_run(self, processing_run_id: uuid.UUID, *, status: str, **kwargs: object) -> Any:
        self.finished.append((processing_run_id, status))
        return SimpleNamespace(status=status)


class _BlobStore:
    def verify_blob(self, **kwargs: object) -> Any:
        raise KeyboardInterrupt


def test_keyboard_interrupt_marks_docx_processing_run_cancelled() -> None:
    sources = _Sources()
    runs = _Runs()
    service = SourceDocxRepresentationService(
        sources=cast(SourceRepository, sources),
        representations=cast(SourceRepresentationRepository, object()),
        blob_store=cast(BlobStore, _BlobStore()),
        representation_store=cast(DocxNativeTextRepresentationStore, object()),
        runs=cast(ModelRunRepository, runs),
        chat=cast(ChatService, _Chat()),
    )

    with pytest.raises(KeyboardInterrupt):
        service.build(sources.source_id)

    assert runs.finished == [(runs.run_id, "cancelled")]
