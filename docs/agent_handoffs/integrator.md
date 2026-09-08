# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `4f077e36248a49d261f13d3f3838d62a376f506f`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0e6fad6c001750f0734adbe48aa45e59690b141d`; spec-core `298bb61c07dd2fdedea0e8a24db30410442c6794`; backend `ac9bf5c289b2979548cfabb9e45a0a9dce51be71`; UI `961786e5f8b65cb88acb415bf756f0905e13d814`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite, auto-merge or main promotion was used.

## Progress this run — integrate UI-GAP-0004 / ERR-0004 Jobs verification-failure copy

UI supplied exact canonical evidence on product/test head `b0c74459af0d6382f23106819f34778c86b6f18b`: Quality run `34240229731 = success`, with Windows path safety, Linux storage, local install smoke, specification validator, Ruff, mypy and full pytest green. The current UI head is a documentation-only descendant of that exact-green product/test head.

Independent compare against current Develop showed the bounded product/test delta consists of `src/athena/desktop/jobs_workspace.py`, `tests/unit/test_pathena_jobs_lifecycle.py`, `tests/unit/test_pathena_jobs_response_copy.py`, and new `tests/unit/test_pathena_jobs_verification_failure_copy.py`. `tests/unit/test_pathena_jobs_status_copy.py` was already aligned on Develop by the prior skip-removal slice and was not rewritten.

Develop commit `33c1dc6f70147d7be2152c4d52b5180f5db44cbb` transplants only those exact verified blobs. Visible verification-failure copy now uses `JOB ACTION COULD NOT BE VERIFIED` and `Diagnostic details` while retaining the diagnostic payload and forbidding implementation-facing headings such as `JOB_ACTION_RESPONSE_UNAVAILABLE` / `Raw command output`. Lifecycle parsing, QProcess spawning, scheduler/worker behavior, persistence, Backend, Storage, Security, Recovery, packaging and Windows-runtime semantics are unchanged.

## Verification state

- UI exact-green product/test head: `b0c74459af0d6382f23106819f34778c86b6f18b`.
- UI canonical Quality: `34240229731 = success`.
- Current UI head `961786e5f8b65cb88acb415bf756f0905e13d814` is ahead of that exact-green head by documentation-only changes; no later product/test mutation exists.
- Develop integration commit: `33c1dc6f70147d7be2152c4d52b5180f5db44cbb`.
- No exact-current-Develop canonical run is claimed yet.

## Error / Alpha-Beta / UI state

- `UI-GAP-0004` is integrated on Develop with exact-green worker evidence; screenshot-level `MATCH` is not claimed because reference pixels remain unavailable.
- ERR-0004 may be closed/reclassified by Error only after consuming this integration evidence and any required exact-Develop verification.
- ERR-0025 remains diagnostic-only until an exact current assertion/root cause is available.
- Spec/Core §75 remains dependent on an exact-green durable Backend Delta prerequisite.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no invented parity percentage is used.

## Next integration order

1. Obtain exact-current-Develop focused Jobs regressions, Ruff and canonical Quality for the descendant carrying `33c1dc6f70147d7be2152c4d52b5180f5db44cbb`.
2. Have Error consume the UI-GAP-0004 / ERR-0004 exact-green integration evidence and close/reclassify only with exact evidence.
3. Consume Backend/Spec-Core current Quality evidence and integrate exactly one compatible READY successor; §75 durable Delta remains the main cross-cutting prerequisite if Backend becomes exact-green.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
