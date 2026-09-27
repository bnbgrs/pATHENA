# Alpha/Beta Integrations + UX seed — Obsidian roundtrip

Date: 2026-09-27
Base Develop: `0c68facde0f7bf9e5d0210925674eb24ddf969bf`
Worker: `fix/alpha-beta-integrations-ux`

## Implemented now
- Projection emits Beta 20 canonical identity fields: `athena_id`, `entity_type`, `revision_id`, `revision_no`, `projection_version`.
- Existing ATHENA-prefixed identity fields remain for transition/backward compatibility.
- Added deterministic parser for managed Knowledge Markdown.
- Added explicit Obsidian reconciliation to a new canonical user revision.
- Stable ID comes only from front matter, never filename.
- Exported expected revision is enforced before write and again atomically by KnowledgeRepository.
- Stale edits conflict instead of overwriting a newer canonical revision.
- Only human title/body are editable in this bounded v1 slice; edits to projected semantic/system metadata fail closed.
- New revision records the exported base revision as provenance input with role `obsidian_projection_base`.
- Added a real polling watcher boundary with a configurable stability window.
- Managed Markdown is read only after size/mtime remain stable across the window and
  a second stat confirms the file did not change during the read.
- Export and watcher share thread-safe SHA-256 write stamps, so ATHENA-authored
  projections are suppressed without weakening external-edit detection.
- Stable external edits are reconciled once; repeated polls do not duplicate revisions.

## Qualification
Run:
- `tests/unit/test_obsidian_projection.py`
- `tests/unit/test_obsidian_export.py`
- `tests/unit/test_obsidian_import.py`
- `tests/unit/test_obsidian_sync.py`
- Knowledge repository/service regressions
- Ruff + mypy

## Remaining Beta 20 work
This does NOT yet claim chapter 20 complete. Next slices remain:
1. runtime composition/start-stop ownership for the polling watcher;
2. three-way merge for provably non-overlapping changes and conflict presentation;
3. new files without ID as explicit import candidates;
4. managed-file deletion intent workflow;
5. optional UI surface for conflicts/import candidates.

UI should be added only when conflict/import-candidate runtime exists. Do not add placeholder controls.
