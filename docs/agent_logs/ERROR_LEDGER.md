# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf` (`feat(jobs): integrate durable schedule recovery`).
- Error worker entered this run at `postmerge/errors@93be775e26a73a57a67fc3ca6d94a65348793e00`.
- Current workers: Spec/Core `39360af3da29101e3038447121ad8d80d11b9f07`; Backend `005dc50b64f72fa143601e6f8d08b2bf39ab701b`; UI `8f28414d1d8649796f1e6ea2e82abf43370e7328`.
- Current Develop canonical Quality: `34706615596@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf = IN_PROGRESS`; no competing canonical run was started by Errors.
- Integrated provenance parent `452547ab46c5d8c678c22c3e1fb9d34652b653fd`: canonical Quality `34703645964 = SUCCESS`.
- Spec/Core exact `39360af3da29101e3038447121ad8d80d11b9f07`: Core Focused Candidate `34704710587 = FAILURE`; canonical Quality `34704710609 = FAILURE`.
- Backend exact `005dc50b64f72fa143601e6f8d08b2bf39ab701b`: Backend Focused Candidate `34706838538 = SUCCESS`; canonical Quality `34706838573 = IN_PROGRESS` at observation time.
- UI exact `8f28414d1d8649796f1e6ea2e82abf43370e7328`: UI Focused Candidate `34706004022 = SUCCESS`; canonical Quality `34706004033 = SUCCESS`. The separate Core Focused workflow on this UI SHA is not treated as a UI product failure.
- `postmerge/errors` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0042`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0042 — Spec/Core revision-change explanation test import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/spec-core@39360af3da29101e3038447121ad8d80d11b9f07`.
- Exact CI: Core Focused Candidate `34704710587 = FAILURE`; canonical Quality `34704710609 = FAILURE`.
- Focused workflow evidence: changed-file Ruff and changed focused unit tests both pass, but the exact remediation-diff guard fails because Ruff would modify the candidate.
- Canonical diagnostics identify exactly one Ruff error: `I001` at `tests/unit/test_revision_change_explanation.py:1:1`, unsorted/unformatted import block. Canonical specification validation, mypy and full pytest are green; full pytest is `4995 passed, 17 skipped`.
- Root cause is therefore bounded test-harness formatting drift in the current Core-owned slice, not a runtime, Storage, Recovery, Windows, packaging or Security regression.
- Ownership: Spec/Core currently owns the slice. Errors must not parallel-edit the Core test while that worker is active.
- Minimal owner repair: organize only the import block in `tests/unit/test_revision_change_explanation.py`, preserve assertions and product behavior, then rerun Core Focused and canonical Quality on the resulting exact SHA.
- Closure requirement: exact worker SHA with both Core Focused and canonical Quality `SUCCESS`; after integration, exact Develop canonical `SUCCESS` carrying the repair before `FIXED`.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; exact root cause was Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1`.
- Owner repair lineage culminated at `postmerge/spec-core@1f61104959dc6a7d7fcff6051fb013f5f6894706`, with Core Focused Candidate `34701843776 = SUCCESS` and canonical Quality `34701843759 = SUCCESS`.
- Integrated closure is now real: `34703645964@develop/pathena-next@452547ab46c5d8c678c22c3e1fb9d34652b653fd = SUCCESS`.
- Do not reopen from older Ruff evidence; require a new current exact-SHA reproduction.

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
