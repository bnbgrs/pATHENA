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

## Qualification
Run:
- `tests/unit/test_obsidian_projection.py`
- `tests/unit/test_obsidian_export.py`
- `tests/unit/test_obsidian_import.py`
- Knowledge repository/service regressions
- Ruff + mypy

## Remaining Beta 20 work
This does NOT yet claim chapter 20 complete. Next slices remain:
1. filesystem watcher + debounce/stability window;
2. write-stamp/hash suppression of self-generated edits;
3. three-way merge for provably non-overlapping changes and conflict presentation;
4. new files without ID as explicit import candidates;
5. managed-file deletion intent workflow;
6. optional UI surface for conflicts/import candidates.

UI should be added only when conflict/import-candidate runtime exists. Do not add placeholder controls.
