"""Core contract for non-canonical Knowledge interpretations.

Interpretations are deliberately distinct from Claims and canonical Knowledge.
User-authored interpretations carry actor provenance. Model-authored
interpretations must carry the exact ModelSignature, ProcessingRun, immutable
input revisions, and pipeline version that produced them.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.common.ids import new_uuid7
from athena.common.time import utc_now_us


class InterpretationOrigin(str, Enum):
    """Semantic authority that authored an interpretation proposal."""

    USER = "user"
    MODEL = "model"


@dataclass(frozen=True, slots=True)
class InterpretationInputRevision:
    """One immutable entity revision used to form an interpretation."""

    entity_id: uuid.UUID
    revision_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.entity_id, uuid.UUID):
            raise TypeError("entity_id must be a UUID")
        if not isinstance(self.revision_id, uuid.UUID):
            raise TypeError("revision_id must be a UUID")


@dataclass(frozen=True, slots=True)
class InterpretationProposal:
    """A provenance-complete interpretation that is not canonical Knowledge.

    Creation of this value never creates or mutates a KnowledgeUnit or Claim.
    Promotion therefore remains a separate semantic commit boundary.
    """

    interpretation_id: uuid.UUID
    created_at_us: int
    text: str
    origin: InterpretationOrigin
    input_revisions: tuple[InterpretationInputRevision, ...]
    actor_id: uuid.UUID | None = None
    model_signature_id: uuid.UUID | None = None
    processing_run_id: uuid.UUID | None = None
    pipeline_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.interpretation_id, uuid.UUID):
            raise TypeError("interpretation_id must be a UUID")
        if isinstance(self.created_at_us, bool) or not isinstance(self.created_at_us, int):
            raise TypeError("created_at_us must be an integer")
        if self.created_at_us < 0:
            raise ValueError("created_at_us must be non-negative")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("interpretation text must not be empty")
        if not isinstance(self.origin, InterpretationOrigin):
            raise TypeError("origin must be an InterpretationOrigin")
        if not isinstance(self.input_revisions, tuple) or any(
            not isinstance(item, InterpretationInputRevision)
            for item in self.input_revisions
        ):
            raise TypeError("input_revisions must contain InterpretationInputRevision values")

        if self.origin is InterpretationOrigin.USER:
            if not isinstance(self.actor_id, uuid.UUID):
                raise ValueError("user interpretations require actor provenance")
            if (
                self.model_signature_id is not None
                or self.processing_run_id is not None
                or self.pipeline_version is not None
            ):
                raise ValueError(
                    "user interpretations must not claim model provenance"
                )
            return

        if self.actor_id is not None:
            raise ValueError("model interpretations must not claim user authorship")
        if not isinstance(self.model_signature_id, uuid.UUID):
            raise ValueError("model interpretations require a ModelSignature")
        if not isinstance(self.processing_run_id, uuid.UUID):
            raise ValueError("model interpretations require a ProcessingRun")
        if not self.input_revisions:
            raise ValueError("model interpretations require immutable input revisions")
        if not isinstance(self.pipeline_version, str) or not self.pipeline_version.strip():
            raise ValueError("model interpretations require a pipeline version")

    @classmethod
    def user(
        cls,
        *,
        text: str,
        actor_id: uuid.UUID,
        input_revisions: tuple[InterpretationInputRevision, ...] = (),
    ) -> InterpretationProposal:
        """Create a user-authored interpretation without model provenance."""

        return cls(
            interpretation_id=new_uuid7(),
            created_at_us=utc_now_us(),
            text=text,
            origin=InterpretationOrigin.USER,
            input_revisions=input_revisions,
            actor_id=actor_id,
        )

    @classmethod
    def model(
        cls,
        *,
        text: str,
        model_signature_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        input_revisions: tuple[InterpretationInputRevision, ...],
        pipeline_version: str,
    ) -> InterpretationProposal:
        """Create a model interpretation with complete immutable provenance."""

        return cls(
            interpretation_id=new_uuid7(),
            created_at_us=utc_now_us(),
            text=text,
            origin=InterpretationOrigin.MODEL,
            input_revisions=input_revisions,
            model_signature_id=model_signature_id,
            processing_run_id=processing_run_id,
            pipeline_version=pipeline_version,
        )
