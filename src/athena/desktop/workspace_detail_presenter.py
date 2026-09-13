"""Presentation-only formatting for desktop detail panes.

The desktop helper CLIs remain the source of truth. These functions only make
successful ``show`` output easier to scan; unknown or continuation lines are
kept verbatim so new CLI fields cannot silently disappear from the UI.
"""

from __future__ import annotations

from collections.abc import Mapping

_RESEARCH_LABELS = {
    "JOB": "Job",
    "STATE": "State",
    "STAGE": "Stage",
    "QUERY": "Query",
    "RETRIES": "Retries",
    "BLOCKED": "Blocked",
    "SCOPE": "Scope",
    "SCOPE_STATE": "Scope state",
    "SNAPSHOT_COMMIT": "Snapshot commit",
    "MODEL": "Model",
    "COVERAGE": "Coverage",
    "COUNTS": "Counts",
    "WORK_ITEMS": "Work items",
}

_JOB_LABELS = {
    "JOB": "Job",
    "TYPE": "Type",
    "STATE": "State",
    "PRIORITY": "Priority",
    "STAGE": "Stage",
    "RETRIES": "Retries",
    "BLOCKED": "Blocked",
    "CREATED_AT_US": "Created at (µs)",
    "UPDATED_AT_US": "Updated at (µs)",
    "NEXT_RUN_AT_US": "Next run at (µs)",
    "WORKER": "Worker",
    "LEASE_ACQUIRED_AT_US": "Lease acquired at (µs)",
    "LEASE_EXPIRES_AT_US": "Lease expires at (µs)",
    "HEARTBEAT_AT_US": "Heartbeat at (µs)",
    "FENCING_SEQUENCE": "Fencing sequence",
    "PROCESSING_RUN": "Processing run",
    "LAST_CHECKPOINT": "Last checkpoint",
    "PROTECTION_SCOPE": "Protection scope",
    "PROTECTED_PAYLOAD": "Protected payload",
    "CHECKPOINTS": "Checkpoints",
}

_SOURCE_LABELS = {
    "SOURCE": "Source",
    "NAME": "Name",
    "TYPE": "Type",
    "MIME": "MIME",
    "BYTES": "Bytes",
    "URI": "URI",
    "CAPTURE_STATE": "Capture state",
    "RETRIEVAL_READINESS": "Retrieval readiness",
    "PROCESSABLE": "Processable",
    "REPRESENTATIONS": "Representations",
    "CHUNKS": "Chunks",
    "PROCESS_JOB": "Process job",
    "PROCESS_STATE": "Process state",
    "PROCESS_STAGE": "Process stage",
    "PROCESS_RETRIES": "Process retries",
    "PROCESS_BLOCKED": "Process blocked",
}


def _field(line: str) -> tuple[str, str] | None:
    """Return a top-level CLI field without interpreting its value."""
    if not line or line[0].isspace():
        return None
    label, separator, value = line.partition(" ")
    if not separator:
        return label, ""
    return label, value


def _append_section(output: list[str], title: str) -> None:
    if output and output[-1] != "":
        output.append("")
    output.append(title)


def _append_known_field(
    output: list[str],
    *,
    label: str,
    value: str,
    labels: Mapping[str, str],
) -> bool:
    display = labels.get(label)
    if display is None:
        return False
    output.append(f"{display}: {value}" if value else f"{display}:")
    return True


def format_research_show(raw: str) -> str:
    """Format successful exhaustive-research ``show`` output for the detail pane."""
    if not raw.strip():
        return raw

    output: list[str] = ["RESEARCH RUN"]
    scope_started = False
    work_started = False

    for line in raw.splitlines():
        parsed = _field(line)
        if parsed is None:
            output.append(line)
            continue
        label, value = parsed

        if label == "SCOPE" and not scope_started:
            _append_section(output, "SCOPE")
            scope_started = True
        elif label == "WORK_ITEMS" and not work_started:
            _append_section(output, "WORK ITEMS")
            work_started = True

        if label == "WORK":
            if not work_started:
                _append_section(output, "WORK ITEMS")
                work_started = True
            output.append(f"• {value}" if value else "•")
            continue

        if not _append_known_field(
            output,
            label=label,
            value=value,
            labels=_RESEARCH_LABELS,
        ):
            output.append(line)

    return "\n".join(output).rstrip()


def format_job_show(raw: str) -> str:
    """Format successful durable-job ``show`` output without hiding diagnostics."""
    if not raw.strip():
        return raw

    output: list[str] = ["JOB"]
    execution_started = False
    checkpoints_started = False

    for line in raw.splitlines():
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if indent and stripped.startswith("PROGRESS "):
            output.append(f"{indent}Progress: {stripped.removeprefix('PROGRESS ')}")
            continue
        if indent and stripped.startswith("RESUME "):
            output.append(f"{indent}Resume: {stripped.removeprefix('RESUME ')}")
            continue

        parsed = _field(line)
        if parsed is None:
            output.append(line)
            continue
        label, value = parsed

        if label == "WORKER" and not execution_started:
            _append_section(output, "EXECUTION")
            execution_started = True
        elif label == "REQUESTED_SCOPE":
            _append_section(output, "REQUESTED SCOPE")
            output.append(value)
            continue
        elif label == "PINNED_CONFIGURATION":
            _append_section(output, "PINNED CONFIGURATION")
            output.append(value)
            continue
        elif label == "CHECKPOINTS" and not checkpoints_started:
            _append_section(output, "CHECKPOINTS")
            checkpoints_started = True

        if label == "CHECKPOINT":
            if not checkpoints_started:
                _append_section(output, "CHECKPOINTS")
                checkpoints_started = True
            output.append(f"• {value}" if value else "•")
            continue

        if not _append_known_field(
            output,
            label=label,
            value=value,
            labels=_JOB_LABELS,
        ):
            output.append(line)

    return "\n".join(output).rstrip()


def format_source_show(raw: str) -> str:
    """Format successful Source ``show`` output while retaining every CLI value."""
    if not raw.strip():
        return raw

    output: list[str] = ["SOURCE"]
    retrieval_started = False
    processing_started = False

    for line in raw.splitlines():
        parsed = _field(line)
        if parsed is None:
            output.append(line)
            continue
        label, value = parsed

        if label == "CAPTURE_STATE" and not retrieval_started:
            _append_section(output, "CAPTURE & RETRIEVAL")
            retrieval_started = True
        elif label == "PROCESS_JOB" and not processing_started:
            _append_section(output, "PROCESSING")
            processing_started = True

        if not _append_known_field(
            output,
            label=label,
            value=value,
            labels=_SOURCE_LABELS,
        ):
            output.append(line)

    return "\n".join(output).rstrip()
