from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ConceptNoteOrigin(StrEnum):
    USER = "user"
    MODEL = "model"


@dataclass(frozen=True, slots=True)
class ConceptNoteRevisionRef:
    entity_id: UUID
    revision_id: UUID


@dataclass(frozen=True, slots=True)
class ConceptNoteProvenance:
    """Immutable provenance contract for a Concept Note revision.

    This object records only references supplied by real upstream services. It does
    not create SourceAnchors, Knowledge revisions, model identities, or actors.
    """

    origin: ConceptNoteOrigin
    input_revisions: tuple[ConceptNoteRevisionRef, ...]
    user_actor_id: UUID | None = None
    model_signature_id: UUID | None = None
    processing_run_id: UUID | None = None
    pipeline_version: str | None = None

    def __post_init__(self) -> None:
        if not self.input_revisions:
            raise ValueError("concept note provenance requires at least one input revision")
        if len(set(self.input_revisions)) != len(self.input_revisions):
            raise ValueError("concept note provenance input revisions must be unique")

        if self.origin is ConceptNoteOrigin.USER:
            if self.user_actor_id is None:
                raise ValueError("user concept note provenance requires user_actor_id")
            if any(
                value is not None
                for value in (
                    self.model_signature_id,
                    self.processing_run_id,
                    self.pipeline_version,
                )
            ):
                raise ValueError("user concept note provenance must not claim model provenance")
            return

        if self.user_actor_id is not None:
            raise ValueError("model concept note provenance must not claim user authorship")
        if self.model_signature_id is None:
            raise ValueError("model concept note provenance requires model_signature_id")
        if self.processing_run_id is None:
            raise ValueError("model concept note provenance requires processing_run_id")
        if self.pipeline_version is None or not self.pipeline_version.strip():
            raise ValueError("model concept note provenance requires pipeline_version")
