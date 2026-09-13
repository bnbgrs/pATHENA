"""Truthful model disclosure for Knowledge revision history surfaces."""

from __future__ import annotations

from dataclasses import dataclass

from athena.knowledge.models import KnowledgeUnitRevision
from athena.model.provenance import ModelSignature, ProcessingRun


@dataclass(frozen=True, slots=True)
class KnowledgeModelDisclosureResponse:
    """Recorded model/run metadata for one Knowledge revision."""

    knowledge_id: str
    revision_id: str
    actor_kind: str
    model_generated: bool
    provider: str | None
    model_identifier: str | None
    model_revision: str | None
    quantization: str | None
    processing_run_id: str | None
    pipeline_version: str | None
    prompt_template_id: str | None
    prompt_template_version: str | None


def disclose_knowledge_revision_model(
    revision: KnowledgeUnitRevision,
    *,
    actor_kind: str,
    processing_run: ProcessingRun | None = None,
    model_signature: ModelSignature | None = None,
) -> KnowledgeModelDisclosureResponse:
    """Project model provenance without inventing participation or linkage."""
    if not isinstance(revision, KnowledgeUnitRevision):
        raise TypeError("revision must be a KnowledgeUnitRevision.")
    if not isinstance(actor_kind, str):
        raise TypeError("actor_kind must be text.")
    normalized_actor_kind = actor_kind.strip()
    if normalized_actor_kind not in {
        "user",
        "primary_model",
        "system",
        "plugin",
        "importer",
        "external_client",
    }:
        raise ValueError("actor_kind is not a recognized provenance actor kind.")

    if normalized_actor_kind == "user":
        if processing_run is not None or model_signature is not None:
            raise ValueError("Direct user Knowledge revisions must not claim model provenance.")
        return _response_without_model(revision, actor_kind=normalized_actor_kind)

    if (processing_run is None) != (model_signature is None):
        raise ValueError("Model disclosure requires ProcessingRun and ModelSignature together.")

    if normalized_actor_kind == "primary_model" and processing_run is None:
        raise ValueError(
            "Primary-model Knowledge revisions require ProcessingRun and ModelSignature."
        )

    if processing_run is None or model_signature is None:
        return _response_without_model(revision, actor_kind=normalized_actor_kind)

    if not isinstance(processing_run, ProcessingRun):
        raise TypeError("processing_run must be a ProcessingRun or None.")
    if not isinstance(model_signature, ModelSignature):
        raise TypeError("model_signature must be a ModelSignature or None.")
    if processing_run.model_signature_id != model_signature.model_signature_id:
        raise ValueError("ProcessingRun references another ModelSignature.")
    if processing_run.status != "succeeded":
        raise ValueError("Knowledge model disclosure requires a succeeded ProcessingRun.")

    return KnowledgeModelDisclosureResponse(
        knowledge_id=str(revision.knowledge_id),
        revision_id=str(revision.revision_id),
        actor_kind=normalized_actor_kind,
        model_generated=True,
        provider=model_signature.provider,
        model_identifier=model_signature.model_identifier,
        model_revision=model_signature.model_revision,
        quantization=model_signature.quantization,
        processing_run_id=str(processing_run.processing_run_id),
        pipeline_version=processing_run.pipeline_version,
        prompt_template_id=processing_run.prompt_template_id,
        prompt_template_version=processing_run.prompt_template_version,
    )


def _response_without_model(
    revision: KnowledgeUnitRevision,
    *,
    actor_kind: str,
) -> KnowledgeModelDisclosureResponse:
    return KnowledgeModelDisclosureResponse(
        knowledge_id=str(revision.knowledge_id),
        revision_id=str(revision.revision_id),
        actor_kind=actor_kind,
        model_generated=False,
        provider=None,
        model_identifier=None,
        model_revision=None,
        quantization=None,
        processing_run_id=None,
        pipeline_version=None,
        prompt_template_id=None,
        prompt_template_version=None,
    )
