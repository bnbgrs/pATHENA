"""Structured presentation for persisted Knowledge and Claim CLI records."""

from __future__ import annotations

from dataclasses import dataclass


class KnowledgeReviewError(ValueError):
    """Raised when persisted detail output cannot be represented truthfully."""


@dataclass(frozen=True)
class ProvenanceReview:
    ordinal: int
    role: str
    entity_id: str
    revision_id: str | None


@dataclass(frozen=True)
class EvidenceReview:
    role: str
    anchor_id: str | None
    message_id: str | None
    entity_id: str | None
    revision_id: str | None
    provenance_id: str


@dataclass(frozen=True)
class KnowledgeEntityReview:
    entity_type: str
    entity_id: str
    lifecycle: str
    revision_no: int
    revision_id: str
    created_at_us: int
    kind: str
    status: str
    content: str
    title: str | None
    provenance: tuple[ProvenanceReview, ...]
    evidence: tuple[EvidenceReview, ...]


def _required(mapping: dict[str, str], key: str) -> str:
    value = mapping.get(key, "").strip()
    if not value or value == "-":
        raise KnowledgeReviewError(f"Persisted detail is missing {key}.")
    return value


def _integer(value: str, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise KnowledgeReviewError(f"Persisted detail has invalid {label}.") from exc
    if parsed < 0:
        raise KnowledgeReviewError(f"Persisted detail has invalid {label}.")
    return parsed


def _optional(value: str) -> str | None:
    return None if value == "-" else value


def _fields(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix + " "):
        raise KnowledgeReviewError(f"Persisted detail expected {prefix}.")
    fields: dict[str, str] = {}
    for token in line[len(prefix) + 1 :].split():
        key, separator, value = token.partition("=")
        if not separator or not key or not value:
            raise KnowledgeReviewError(f"Persisted {prefix} field is invalid.")
        fields[key] = value
    return fields


def parse_knowledge_entity_review(output: str) -> KnowledgeEntityReview:
    """Parse the exact line protocol emitted by ``knowledge_cli show`` commands."""
    lines = output.splitlines()
    if len(lines) < 10:
        raise KnowledgeReviewError("Persisted detail output is incomplete.")
    identity = lines[0].split(" ", 1)
    if len(identity) != 2 or identity[0] not in {"KNOWLEDGE", "CLAIM"}:
        raise KnowledgeReviewError("Persisted detail identity is invalid.")
    entity_type, entity_id = identity
    content_marker = "BODY" if entity_type == "KNOWLEDGE" else "STATEMENT"
    try:
        content_index = lines.index(content_marker)
        provenance_index = next(
            index
            for index in range(content_index + 1, len(lines))
            if lines[index].startswith("PROVENANCE_INPUTS ")
        )
    except (ValueError, StopIteration) as exc:
        raise KnowledgeReviewError("Persisted detail content boundary is invalid.") from exc

    header: dict[str, str] = {}
    for line in lines[1:content_index]:
        key, separator, value = line.partition(" ")
        if not separator:
            raise KnowledgeReviewError("Persisted detail header is invalid.")
        header[key] = value
    revision = _required(header, "REVISION").split()
    if len(revision) != 2:
        raise KnowledgeReviewError("Persisted detail revision is invalid.")
    content = "\n".join(lines[content_index + 1 : provenance_index]).strip()
    if not content:
        raise KnowledgeReviewError("Persisted detail content is empty.")

    provenance_count = _integer(
        lines[provenance_index].split(" ", 1)[1], "provenance count"
    )
    evidence_index = next(
        (
            index
            for index in range(provenance_index + 1, len(lines))
            if lines[index].startswith("EVIDENCE ")
        ),
        len(lines),
    )
    provenance: list[ProvenanceReview] = []
    for line in lines[provenance_index + 1 : evidence_index]:
        parts = line.split(maxsplit=2)
        if len(parts) != 3 or parts[0] != "PROVENANCE":
            raise KnowledgeReviewError("Persisted provenance record is invalid.")
        ordinal_text = parts[1]
        fields = _fields("PROVENANCE " + parts[2], "PROVENANCE")
        provenance.append(
            ProvenanceReview(
                ordinal=_integer(ordinal_text, "provenance ordinal"),
                role=_required(fields, "role"),
                entity_id=_required(fields, "entity"),
                revision_id=_optional(fields.get("revision", "-")),
            )
        )
    if len(provenance) != provenance_count:
        raise KnowledgeReviewError("Persisted provenance count does not match its records.")

    evidence: list[EvidenceReview] = []
    if evidence_index < len(lines):
        evidence_count = _integer(
            lines[evidence_index].split(" ", 1)[1], "evidence count"
        )
        for line in lines[evidence_index + 1 :]:
            fields = _fields(line, "EVIDENCE_REF")
            evidence.append(
                EvidenceReview(
                    role=_required(fields, "role"),
                    anchor_id=_optional(fields.get("anchor", "-")),
                    message_id=_optional(fields.get("message", "-")),
                    entity_id=_optional(fields.get("entity", "-")),
                    revision_id=_optional(fields.get("revision", "-")),
                    provenance_id=_required(fields, "provenance"),
                )
            )
        if len(evidence) != evidence_count:
            raise KnowledgeReviewError("Persisted evidence count does not match its records.")

    return KnowledgeEntityReview(
        entity_type=entity_type.casefold(),
        entity_id=entity_id,
        lifecycle=_required(header, "LIFECYCLE"),
        revision_no=_integer(revision[0], "revision number"),
        revision_id=revision[1],
        created_at_us=_integer(_required(header, "CREATED_AT_US"), "creation time"),
        kind=_required(header, "KIND"),
        status=_required(header, "STATUS"),
        content=content,
        title=_optional(header.get("TITLE", "-")) if entity_type == "KNOWLEDGE" else None,
        provenance=tuple(provenance),
        evidence=tuple(evidence),
    )


def _short(value: str) -> str:
    return value[:8].upper()


def render_knowledge_entity_review(review: KnowledgeEntityReview) -> str:
    """Render only persisted fields with compact provenance-first hierarchy."""
    label = "KNOWLEDGE" if review.entity_type == "knowledge" else "CLAIM"
    lines = [
        label,
        review.title or review.content,
        "",
        "CONTENT",
        review.content,
        "",
        "STATE",
        f"{review.kind.replace('_', ' ').title()} · {review.status.replace('_', ' ').title()} · {review.lifecycle.replace('_', ' ').title()}",
        "",
        "PROVENANCE",
    ]
    if not review.provenance:
        lines.append("No provenance inputs were persisted for this revision.")
    for provenance_item in review.provenance:
        revision = (
            ""
            if provenance_item.revision_id is None
            else f" · revision {_short(provenance_item.revision_id)}"
        )
        lines.append(
            f"{provenance_item.ordinal + 1:02d} · "
            f"{provenance_item.role.replace('_', ' ')} · "
            f"{_short(provenance_item.entity_id)}{revision}"
        )
    if review.entity_type == "claim":
        lines.extend(("", "EVIDENCE"))
        if not review.evidence:
            lines.append("No evidence references were persisted for this claim.")
        for evidence_item in review.evidence:
            references = tuple(
                value
                for value in (
                    evidence_item.anchor_id,
                    evidence_item.message_id,
                    evidence_item.entity_id,
                    evidence_item.revision_id,
                )
                if value is not None
            )
            suffix = " · ".join(_short(value) for value in references) or "no direct anchor"
            lines.append(f"{evidence_item.role.replace('_', ' ')} · {suffix}")
    lines.extend(
        (
            "",
            f"{label.title()} {_short(review.entity_id)} · Revision {review.revision_no} {_short(review.revision_id)}",
        )
    )
    return "\n".join(lines)
