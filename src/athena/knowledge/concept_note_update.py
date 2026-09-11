from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from athena.knowledge.concept_note_provenance import ConceptNoteRevisionRef


class ConceptNoteChangeRelevance(StrEnum):
    """Upstream semantic assessment of newly available note inputs."""

    UNKNOWN = "unknown"
    IRRELEVANT = "irrelevant"
    RELEVANT = "relevant"


class ConceptNoteUpdateAction(StrEnum):
    """Fail-closed action emitted by the Concept Note update policy."""

    KEEP_CURRENT = "keep_current"
    PROPOSE_UPDATE = "propose_update"


@dataclass(frozen=True, slots=True)
class ConceptNoteUpdateDecision:
    """Derived decision; never a canonical write instruction."""

    action: ConceptNoteUpdateAction
    new_input_revisions: tuple[ConceptNoteRevisionRef, ...]
    reason: str


class ConceptNoteUpdatePolicy:
    """Prevent blind Concept Note rewrites when upstream inputs change.

    The policy consumes only real revision references supplied by callers. It never
    creates revisions, provenance, or content. Even a relevant change yields an
    update proposal; committing a new Concept Note revision remains a separate
    semantic workflow.
    """

    def decide(
        self,
        *,
        current_inputs: tuple[ConceptNoteRevisionRef, ...],
        candidate_inputs: tuple[ConceptNoteRevisionRef, ...],
        relevance: ConceptNoteChangeRelevance,
    ) -> ConceptNoteUpdateDecision:
        self._validate_inputs("current_inputs", current_inputs)
        self._validate_inputs("candidate_inputs", candidate_inputs)
        if not isinstance(relevance, ConceptNoteChangeRelevance):
            raise TypeError("relevance must be a ConceptNoteChangeRelevance")

        current = set(current_inputs)
        new_inputs = tuple(item for item in candidate_inputs if item not in current)
        if not new_inputs:
            return ConceptNoteUpdateDecision(
                action=ConceptNoteUpdateAction.KEEP_CURRENT,
                new_input_revisions=(),
                reason="no_new_input_revisions",
            )
        if relevance is not ConceptNoteChangeRelevance.RELEVANT:
            return ConceptNoteUpdateDecision(
                action=ConceptNoteUpdateAction.KEEP_CURRENT,
                new_input_revisions=new_inputs,
                reason=(
                    "relevance_not_confirmed"
                    if relevance is ConceptNoteChangeRelevance.UNKNOWN
                    else "new_inputs_not_relevant"
                ),
            )
        return ConceptNoteUpdateDecision(
            action=ConceptNoteUpdateAction.PROPOSE_UPDATE,
            new_input_revisions=new_inputs,
            reason="relevant_new_input_revisions",
        )

    @staticmethod
    def _validate_inputs(
        label: str,
        values: tuple[ConceptNoteRevisionRef, ...],
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{label} must be a tuple")
        if any(not isinstance(item, ConceptNoteRevisionRef) for item in values):
            raise TypeError(f"{label} must contain ConceptNoteRevisionRef values")
        if len(set(values)) != len(values):
            raise ValueError(f"{label} must not contain duplicate revision references")
