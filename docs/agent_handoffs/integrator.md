# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `c487df792b0aaa6af9a4a48a848b07bfd20a8eef`; spec-core `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`; backend `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; UI `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Integrated this run — UI-GAP-0073

The exact-green bounded Jobs copy slice was independently reviewed and transplanted onto current Develop without importing divergent UI history.

- UI product commit: `4315a744a097c35ab46be4df883f0853544446b9`.
- UI focused regression: `cf777ca08ac0885c636aed95b5f6ddd6cd381386`.
- Verified UI worker head: `352b4c72c39d5cafe866c604a050a1b93df71940`.
- Canonical ATHENA Quality: `34174030199 = success` on that exact worker head.
- Develop integration commit: `257ac625a66b8295cc8a3caba3a0a669a558e25e`.
- Exact worker blobs transplanted: `src/athena/desktop/jobs_workspace.py@a17b7111f6d6c826cf38f57c885b60ac3c550146` and `tests/unit/test_pathena_jobs_status_copy.py@a1ba67fdf864f49945a7dd5c6e3bfe9b981d09bd`.
- Product delta is copy-only: `Refreshing jobs`, `Requesting cancellation`, `Loading job details`, `Jobs refreshed`, and `Job … details loaded` replace persistence-oriented wording.
- The focused real-Qt regression locks progress/success copy and rejects `durable`/`persisting` leakage. The verified harness restores the original `refresh()` method after constructor suppression; no assertion or product behavior is weakened.
- Job lifecycle, transition receipt, persistence, Storage, scheduler/worker, provider/transport, Security, cancellation and process-spawn semantics are unchanged.

## Verification / READY state

- UI-GAP-0073 exact worker Quality `34174030199`: SUCCESS.
- Current Develop integration commit `257ac625a66b8295cc8a3caba3a0a669a558e25e`: no associated exact workflow run observed yet; global-green/promotion-ready is not claimed.
- Spec/Core `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`: canonical Quality `34176070442 = success`; the only final delta is Ruff import grouping in `tests/unit/test_exhaustive_research_large_archive.py`. This makes the bounded Large Archive acceptance lineage a candidate for independent next-run integration review.
- Backend product/test head `98f7cb035c435d72732726e2948b9883f07bbfe5`: Quality `34177033443 = cancelled`; not READY.
- UI current handoff head `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`: Quality `34177763716 = pending`; UI-GAP-0074 not READY.
- No Skip/XFail, weakened assertions or relaxed Security/Storage/Windows/Recovery/validator guard was introduced.

## Error state

- Error handoff currently records `ERR-0021` and `ERR-0022` IN_PROGRESS.
- `ERR-0022` was Ruff-only on predecessor Spec/Core SHA `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`; exact successor `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5` is now canonical-green (`34176070442`). Treat closure as evidence-backed pending error-handoff synchronization, not as a product defect.
- `ERR-0021` remains unresolved because current Develop has no exact completed canonical run and the prior full-pytest-only shared-baseline signal lacks exposed traceback evidence.
- Historical Windows/runtime crash classes remain Beta/release regression obligations only absent exact-current reproduction.

## UI / Alpha-Beta state

- Eleven-screen manifest remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`; original reference images are unavailable through the current repository/tool path, so no `MATCH` claim is permitted.
- UI-GAP-0073 is now integrated with exact-green worker evidence.
- UI-GAP-0074 remains `IMPLEMENTED_PENDING_VERIFY` until exact canonical success.
- `docs/development/ALPHA_BETA_PROGRESS.md` was read, but its complete large-file body is not safely exposed by the connector in one non-destructive write surface. No partial destructive rewrite was attempted; this handoff is the exact versioned integration evidence for later tracker synchronization.
- No percentage progress is inferred.

## Next integration order

1. Obtain exact-current-Develop canonical Quality for `257ac625a66b8295cc8a3caba3a0a669a558e25e` or a product-identical documentation descendant.
2. Independently review the exact-green Spec/Core Large Archive lineage ending at `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`; integrate only its bounded acceptance/test delta if compatible with Develop.
3. Backend worker-ID hardening remains excluded until a successful exact canonical run replaces cancelled `34177033443`.
4. UI-GAP-0074 remains excluded while `34177763716` is pending.
5. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
