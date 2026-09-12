# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf` (`feat(jobs): integrate durable schedule recovery`).
- Error worker entered this run at `postmerge/errors@3f7f5e35b2248688de4203c1f072e8a9cda92dbc`.
- Current workers: Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `c5151466928dbe751a2e62c210717d0858a74bd3`; UI `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`.
- Current Develop canonical Quality: `34706615596@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf = IN_PROGRESS`; Errors started no competing canonical run.
- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`: Core Focused Candidate `34709904332 = FAILURE`; canonical Quality `34709904327 = IN_PROGRESS` at observation time, with canonical Ruff already failed while specification validator, Windows path safety, Linux storage regressions and Local Install were green.
- Backend exact `c5151466928dbe751a2e62c210717d0858a74bd3`: Backend Focused Candidate `34708379912 = SUCCESS`; Storage Focused Candidate `34708379880 = FAILURE`; canonical Quality `34708379877 = IN_PROGRESS`. On that canonical run, specification validator, Ruff, mypy, Linux storage regressions, Windows path safety/release guards and Local Install were green while full pytest remained running.
- UI exact `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`: canonical Quality `34709115225 = IN_PROGRESS`; a separate Core Focused Candidate `34709115243 = FAILURE`. The Core-focused failure is not classified as an independent UI product defect without exact diagnostics.
- `postmerge/errors@3f7f5e35b2248688de4203c1f072e8a9cda92dbc` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0042`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0042 — current Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Historical current-run reproducer predecessor: `postmerge/spec-core@39360af3da29101e3038447121ad8d80d11b9f07`, where canonical diagnostics identified Ruff `I001` at `tests/unit/test_revision_change_explanation.py:1:1` and full pytest was `4995 passed, 17 skipped`.
- Owner attempted repair: `postmerge/spec-core@f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb` (`fix(core): normalize revision change import`). The commit changed only `tests/unit/test_revision_change_explanation.py`, expanding the `revision_change_explanation` import into a parenthesized multiline import and leaving product behavior/assertions unchanged.
- Exact successor evidence: Core Focused Candidate `34709904332 = FAILURE`. The changed focused unit tests themselves complete successfully, but Ruff outcome remains failure; the remediation-diff step therefore executes and the final focused enforcement fails. This proves the first owner formatting repair is insufficient on the exact successor SHA.
- Canonical exact successor `34709904327` was still running at observation time, but canonical Ruff had already failed; specification validator, Windows path safety, Linux storage regressions and Local Install were green. No `FIXED_PENDING_VERIFY` or `FIXED` claim is permitted.
- Current net diff from the PR base `5eecb5f937de9325a9673df5f1a23d2f1b5e87cf` is bounded to `src/athena/knowledge/revision_change_explanation.py` and `tests/unit/test_revision_change_explanation.py`. This remains Core-owned; Errors must not parallel-edit while the worker owns the slice.
- Required next evidence: consume the exact Ruff diagnostics/remediation for `f86df7dc...`, apply only the exact Ruff-required import correction on Spec/Core, then require Core Focused and canonical Quality `SUCCESS` on one unchanged exact worker SHA; after integration require exact Develop canonical `SUCCESS` before `FIXED`.

## Current exact failures not yet promoted to ERR IDs

### Backend Storage Focused `34708379880@c5151466928dbe751a2e62c210717d0858a74bd3`

- Current and exact, but not yet root-caused enough for a new stable `ERR-*`.
- The workflow's final enforcement is red while its displayed Ruff, mypy and Storage-test steps are all marked completed/success because those steps use `continue-on-error`; exact step outcome must be taken from the focused diagnostics rather than inferred from display conclusions.
- Canonical evidence on the same SHA already has Ruff, mypy, Linux storage regressions, Windows release guards and Local Install green; full pytest was still running. Therefore do not classify this as a general Storage/Recovery guard regression without the exact hidden sub-outcome/diagnostic artifact.
- The candidate product delta is bounded to validated concurrent WAL/SHM publication revalidation plus a focused startup-identity test; no guard weakening may be used to clear the focused failure.

### UI Core Focused `34709115243@1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`

- Current and exact, but not a proven UI product root cause. The Core-focused workflow's Ruff outcome is failure and remediation runs, while focused tests complete; canonical Quality on the same UI SHA remains in progress.
- UI branch net changes include UI/harness work plus Core-path history relative to its PR base, so the red Core-focused workflow must be diagnosed from exact remediation evidence before creating a UI or Core error ID. Do not duplicate `ERR-0042` without proving the same Ruff signature.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; exact root cause was Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1`.
- Owner repair lineage culminated at `postmerge/spec-core@1f61104959dc6a7d7fcff6051fb013f5f6894706`, with Core Focused Candidate `34701843776 = SUCCESS` and canonical Quality `34701843759 = SUCCESS`.
- Integrated closure: `34703645964@develop/pathena-next@452547ab46c5d8c678c22c3e1fb9d34652b653fd = SUCCESS`.

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
