"""Short-lived desktop process adapter for explicit Obsidian Knowledge export."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

from athena.core.application import AthenaApplication
from athena.knowledge.obsidian_export import (
    ObsidianConflictPolicy,
    ObsidianExportConflictError,
    ObsidianVaultExporter,
)
from athena.knowledge.obsidian_projection import ObsidianNote, project_knowledge_snapshot
from athena.storage.durable_fs import is_link_boundary


@dataclass(frozen=True, slots=True)
class ObsidianExportPreview:
    """Read-only export intent shown before any filesystem mutation."""

    relative_path: str
    destination: str
    state: str
    detail: str
    replace_required: bool


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-knowledge-obsidian-export")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "export"):
        action = commands.add_parser(command)
        action.add_argument("knowledge_id", type=uuid.UUID)
        action.add_argument("--vault", required=True)
        if command == "export":
            action.add_argument("--replace", action="store_true")
    return parser


def _destination(exporter: ObsidianVaultExporter, note: ObsidianNote) -> Path:
    raw = note.relative_path
    if not raw or "\\" in raw:
        raise ValueError("Obsidian projection returned an invalid relative path.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} or ":" in part for part in parts):
        raise ValueError("Obsidian projection returned an unsafe relative path.")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or relative.anchor:
        raise ValueError("Obsidian projection escaped the selected vault.")
    destination = exporter.vault_root.joinpath(*relative.parts)
    destination.relative_to(exporter.vault_root)
    return destination


def _assert_preview_parent_safe(vault_root: Path, destination: Path) -> None:
    relative_parent = destination.parent.relative_to(vault_root)
    cursor = vault_root
    for part in relative_parent.parts:
        cursor = cursor / part
        if not cursor.exists() and not is_link_boundary(cursor):
            return
        if is_link_boundary(cursor) or not cursor.is_dir():
            raise NotADirectoryError(
                f"Obsidian export parent is an unsafe filesystem boundary: {cursor}"
            )


def preview_note(vault_root: Path, note: ObsidianNote) -> ObsidianExportPreview:
    """Inspect one deterministic projection without creating or replacing anything."""

    exporter = ObsidianVaultExporter(vault_root)
    destination = _destination(exporter, note)
    _assert_preview_parent_safe(exporter.vault_root, destination)
    payload = note.markdown.encode("utf-8")

    if is_link_boundary(destination):
        return ObsidianExportPreview(
            relative_path=note.relative_path,
            destination=str(destination),
            state="blocked",
            detail="Destination is a symlink or reparse point.",
            replace_required=False,
        )
    if not destination.exists():
        return ObsidianExportPreview(
            relative_path=note.relative_path,
            destination=str(destination),
            state="create",
            detail="A new local Markdown projection will be created.",
            replace_required=False,
        )
    if not destination.is_file():
        return ObsidianExportPreview(
            relative_path=note.relative_path,
            destination=str(destination),
            state="blocked",
            detail="Destination exists but is not a regular file.",
            replace_required=False,
        )
    if destination.read_bytes() == payload:
        return ObsidianExportPreview(
            relative_path=note.relative_path,
            destination=str(destination),
            state="unchanged",
            detail="Existing note already matches the canonical projection.",
            replace_required=False,
        )
    return ObsidianExportPreview(
        relative_path=note.relative_path,
        destination=str(destination),
        state="conflict",
        detail="Existing note differs; explicit replacement is required.",
        replace_required=True,
    )


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    snapshot = app.knowledge.load(args.knowledge_id)
    note = project_knowledge_snapshot(snapshot)
    vault = Path(args.vault)

    if args.command == "preview":
        _emit({"kind": "preview", **asdict(preview_note(vault, note))})
        return 0

    policy = (
        ObsidianConflictPolicy.REPLACE
        if bool(args.replace)
        else ObsidianConflictPolicy.KEEP_IDENTICAL
    )
    exporter = ObsidianVaultExporter(vault)
    result = exporter.export_note(note, conflict_policy=policy)
    _emit(
        {
            "kind": "result",
            "relative_path": note.relative_path,
            "destination": str(result.path),
            "status": result.status.value,
            "policy": policy.value,
        }
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except (ObsidianExportConflictError, OSError, TypeError, ValueError) as exc:
        _emit({"kind": "error", "error": type(exc).__name__, "detail": str(exc)})
        return 2
    except Exception as exc:
        print(f"OBSIDIAN_EXPORT_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
