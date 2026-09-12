# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before the current integration: `522a01050dba5b4dafa81d60573bd185a8e7e15b`.
- Exact parent canonical Quality: `34712404459 = FAILURE`.
- Exact failure is bounded to canonical Ruff I001 in `tests/unit/test_core_focused_candidate_workflow.py`; Windows path safety, Linux storage regressions, Local install smoke and full pytest passed on the same SHA.
- Current worker heads checked:
  - Errors: `cc856567b5e7c05c8b36e919cddb7808476f366a`
  - Spec/Core: `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`
  - Backend: `365df03a040cb9dffddf6f942ae61a2cdb8dc375`
  - UI: `6bc46a2464344d56ca00461df30ba4a619437498`

## Current integration state

- Durable schedule identity primitives, scheduled-job materialization, and durable schedule recovery remain integrated on Develop.
- Source-free user Knowledge, user-correction conflict visibility, and truthful Knowledge provenance explanation remain integrated.
- Fail-closed release-readiness assessment remains integrated.
- Core Focused candidate selection excludes deleted paths and preserves tracked-worktree remediation guards.
- The dedicated workflow-regression test introduced at `522a010...` is behaviorally intact; the current slice corrects only its Ruff I001 import-block formatting regression.

## Worker readiness snapshot

- Spec/Core `9f2052b9...` is NOT READY because exact Core Focused and canonical Quality are red.
- Backend `365df03a...` remains conservative pending exact-green Storage Focused and canonical evidence for the sidecar-preflight successor.
- UI `6bc46a24...` requires exact-current bounded candidate evidence; synchronization/head movement is not itself promotions evidence.
- Errors remains diagnostic and must not override newer exact-head workflow evidence.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` keeps all eleven slots at `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no `MATCH` is inferred without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise makes no screenshot-level `MATCH` claim.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap regression signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
