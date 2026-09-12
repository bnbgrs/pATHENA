# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before the current integration: `b8afe9661387c4a1a3d65f539c39ca772f37329c`.
- Exact parent canonical Quality: `34710920451 = SUCCESS`.
- Current worker heads checked:
  - Errors: `3e3915d5cb0c3964661db1fcef100f98664915c1`
  - Spec/Core: `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`
  - Backend: `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`
  - UI: `460e35e74d8c529a5880356bf30b9099d80e39de`

## Current integration state

- Durable schedule identity primitives, scheduled-job materialization, and durable schedule recovery remain integrated on Develop.
- Source-free user Knowledge, user-correction conflict visibility, and truthful Knowledge provenance explanation remain integrated.
- Fail-closed release-readiness assessment remains integrated.
- Core Focused candidate selection already excludes deleted paths and preserves tracked-worktree remediation guards.
- Current cross-cutting slice adds a repository regression test that locks those workflow invariants against silent reintroduction of deletion-inclusive selection or dirty tracked remediation.

## Worker readiness snapshot

- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb` is NOT READY: focused behavior tests pass but exact Ruff I001 remains.
- Backend exact `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` is NOT READY: Backend Focused is green while Storage Focused is red on sidecar identity continuity.
- UI exact `460e35e74d8c529a5880356bf30b9099d80e39de` has green UI Focused evidence but canonical Quality is still active, so no stale READY classification is made.
- Errors evidence remains useful for root-cause classification but its documented baseline trails current Develop.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains fail-closed; no `MATCH` is inferred without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise makes no screenshot-level `MATCH` claim.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap regression signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
