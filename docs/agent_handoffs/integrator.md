# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `ea77cc03ce1d5c6a27286ac6c7cba38a7ce6566e`; spec-core `07263cc7474954f1591523077caa8eb8532605dd`; backend `8964f9ae22f0b3f98d06f9c000a47a98dc54f473`; ui `0d5a89b879ee0959a42734181adb129f4c3de024`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite or auto-merge was used.

## Integrated this run — UI-GAP-0039 Sources detail keyboard focus

The current UI handoff marks UI-GAP-0039 `FIXED / INTEGRATOR_READY`. Product commit `6d2d0eb32fa0bcd6b2c1112070a36ce1401f6bfa` adds only `QPlainTextEdit#sourceDetails:focus` to the canonical accent-border focus selector block. Focused regression `57636da80d3f3db586d1d728b4e6d39dd11896bd` locks the selector and canonical accent token. Exact UI lineage Quality `34031028328` succeeded.

Only the independently reviewed bounded delta was applied to Develop:

- product `f179eed4bc37d81532c4cc6c8f3f5206e4e80aed`;
- focused regression `adc9bea487b80bcacd077e4cfb6eca7965831b6b`.

Compare `be0e8da5127f17f6bbc3cbbc8c58496102c9135c..adc9bea487b80bcacd077e4cfb6eca7965831b6b` is ahead 2 / behind 0 and changes exactly two files: `src/athena/desktop/pathena_shared_components.py` +1 and new `tests/unit/test_pathena_sources_detail_focus.py` +10. Divergent UI history and unrelated later selectors were not imported.

## Validation and error state

- UI source lineage canonical Quality `34031028328 = success`.
- Focused regression is included in that exact green UI lineage.
- Exact-current-Develop global Quality is not claimed; no exact head run was observed during this integration.
- Error handoff now records `ERR-0016` and `ERR-0017` as `FIXED` on corrected-lineage Quality `34030367660`; `ERR-0014` remains `STALE`; no current OPEN error is recorded.

## UI state

- UI-GAP-0039 is integrated on Develop.
- Current UI handoff marks UI-GAP-0040 `IMPLEMENTED_PENDING_VERIFY`; it is not READY until its own exact canonical Quality succeeds.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no pixel-level `MATCH` claim is valid while original reference images remain pending.

## Alpha/Beta progress

`docs/development/ALPHA_BETA_PROGRESS.md` was read. Retrieval, contradiction, Research, Storage and Local HTTP verified contracts remain recorded. Complete connector retrieval of the tracker is truncated, so this run did not replace the whole file and risk data loss. UI-GAP-0039 integration evidence is versioned here pending safe tracker reconciliation.

## Next integration order

1. Prefer a newer bounded exact-green Core successor if compatible with current Develop.
2. Otherwise consume exactly one READY Backend/UI successor; UI-GAP-0040 remains excluded until canonical green evidence exists.
3. Obtain exact-current-Develop canonical Quality before any promotion/readiness claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
