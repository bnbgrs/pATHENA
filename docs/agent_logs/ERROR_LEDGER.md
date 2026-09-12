# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@db159a068a5de1ca8cd302a5ea436f3f07889d9f` (`fix(release): normalize readiness Ruff formatting`).
- Error worker entered this run at `postmerge/errors@e33839260e5582e972aa6e311c9631afbe08fe24`.
- Current workers: Spec/Core `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `9e9227dc722d7d771ae4ce4e45a75983330fed97`.
- Develop canonical Quality: `34700628139@db159a068a5de1ca8cd302a5ea436f3f07889d9f = IN_PROGRESS`; no competing canonical run was started.
- Parent Develop `146fb7280dbfe30f2bec129aec8ee77f015ce040`: canonical `34697870543 = FAILURE`, isolated to Ruff in the release-readiness slice; specification validator, mypy, full pytest, Windows path safety/release guards, Linux storage regressions and local install passed.
- Spec/Core exact `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`: Core Focused `34698818610 = SUCCESS`; canonical `34698818608 = FAILURE`.
- Backend exact `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`: Backend Focused `34700396671 = SUCCESS`; canonical `34700396666 = IN_PROGRESS` at observation time.
- UI exact `9e9227dc722d7d771ae4ce4e45a75983330fed97`: UI Focused `34699977144 = SUCCESS`; cumulative Core Focused `34699977166 = FAILURE`.
- `postmerge/errors@e33839260e5582e972aa6e311c9631afbe08fe24` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0041`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; Core Focused `34696122597 = FAILURE`, canonical `34696122599 = FAILURE`; exact root cause was Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1`.
- Owner repair exact SHA: `postmerge/spec-core@a35a67f1afe2789d8a568fa3484ef5fe29f46de9`. The file now has the standard-library import block ordered with `import uuid` before `dataclasses`/`datetime` imports.
- Focused owner verification: Core Focused `34698818610 = SUCCESS` on exact repair SHA.
- Canonical `34698818608@a35a67f1afe2789d8a568fa3484ef5fe29f46de9 = FAILURE`, but downloaded exact-SHA diagnostics show the remaining two Ruff `I001` failures are exclusively `src/athena/release_readiness.py:3:1` and `tests/unit/test_release_readiness.py:1:1`; the provenance file is no longer reported.
- Therefore the original ERR-0041 root cause is repaired on its owning worker and is not the cause of that canonical failure. Do not conflate the inherited release-readiness Ruff drift with ERR-0041.
- Current Develop `db159a068a5de1ca8cd302a5ea436f3f07889d9f` contains a bounded repair for those release-readiness Ruff blocks; its canonical `34700628139` is still running.
- Closure requirement: a current/superseding integrated exact SHA carrying the provenance repair with successful canonical verification. Until then retain `FIXED_PENDING_VERIFY`, not `FIXED`.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; root-cause repair `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13`.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical `34693685375 = SUCCESS`.
- Integrated closure: `34694827693@develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34680853488@develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34666307002@develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

## ERR-0039 / ERR-0038

Both are `STALE`; historical Spec/Core Ruff failures are superseded and may be reopened only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or removed guard is current.
