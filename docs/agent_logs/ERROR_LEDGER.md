# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf` (`feat(jobs): integrate durable schedule recovery`).
- Error worker entered this run at `postmerge/errors@3f7f5e35b2248688de4203c1f072e8a9cda92dbc`; current pre-ledger-update worker head was `261fc5213330c7abdd12c29c11677437604806fc`.
- Current workers: Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `c5151466928dbe751a2e62c210717d0858a74bd3`; UI `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`.
- Current Develop canonical Quality: `34706615596@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf = IN_PROGRESS`; Errors started no competing canonical run.
- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`: Core Focused Candidate `34709904332 = FAILURE`; canonical Quality `34709904327 = IN_PROGRESS` at observation time, with canonical Ruff already failed while specification validator, Windows path safety, Linux storage regressions and Local Install were green.
- Backend exact `c5151466928dbe751a2e62c210717d0858a74bd3`: Backend Focused Candidate `34708379912 = SUCCESS`; Storage Focused Candidate `34708379880 = FAILURE`; canonical Quality `34708379877 = IN_PROGRESS`. Canonical specification validator, Ruff, mypy, Linux storage regressions, Windows path safety/release guards and Local Install were green while full pytest remained running.
- UI exact `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`: canonical Quality `34709115225 = IN_PROGRESS`; separate Core Focused Candidate `34709115243 = FAILURE`.
- `postmerge/errors@261fc5213330c7abdd12c29c11677437604806fc` had zero workflow runs before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0042`, `ERR-0043`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0043 — Backend SQLite startup revalidation accepts foreign sidecar replacement

- Severity: P1 Storage/release integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/backend@c5151466928dbe751a2e62c210717d0858a74bd3` (`fix(storage): tolerate validated concurrent WAL publication`).
- Exact CI: Storage Focused Candidate `34708379880 = FAILURE`; Backend Focused Candidate `34708379912 = SUCCESS`; canonical Quality `34708379877 = IN_PROGRESS` at observation time.
- Exact downloaded Storage-focused diagnostics are unambiguous: Ruff passes; Storage mypy passes (`Success: no issues found in 35 source files`); focused pytest fails `2 failed, 29 passed`.
- Failure 1 is release-guard relevant: `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` expected `DatabaseStartupIdentityChangedError`, but no exception was raised after replacing the preflight WAL sidecar with literal `b"foreign-sidecar"` bytes. The current `_revalidate_existing_identity()` only requires unchanged primary DB identity, re-inspects the file set, and accepts the refreshed sidecar identity. This weakens the prior fail-closed DB/WAL/SHM identity continuity invariant.
- Failure 2 proves the newly added positive test is not a valid reproducer of the intended concurrent-publication case: `test_bound_preflight_accepts_valid_concurrent_sidecar_publication` asserts `published_identity != original_identity`, but both identities are exactly equal. `_create_current_database()` already leaves the WAL/SHM identities present, so opening another connection does not publish a new identity in this fixture.
- Root-cause cluster is therefore one bounded Backend-owned change: the implementation cannot distinguish a legitimate newly published sidecar from a foreign/replaced existing sidecar, while its positive test currently does not construct the intended identity transition.
- Required safe repair: restore fail-closed rejection for replacement of any sidecar identity that existed at preflight. If legitimate concurrent publication must be accepted, constrain it to a demonstrably absent-at-preflight -> validly published sidecar transition and validate that transition without accepting arbitrary/replaced bytes. The positive test must first construct and prove that exact transition. Do not relax `assert_database_file_set_identity`, Recovery/Storage guards, or the negative sidecar-substitution test.
- Closure requirement: exact Backend/Storage focused tests green, canonical Quality green on the unchanged owner SHA, then integrated Develop canonical green before `FIXED`.

## ERR-0042 — current Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Historical current-run reproducer predecessor: `postmerge/spec-core@39360af3da29101e3038447121ad8d80d11b9f07`, where canonical diagnostics identified Ruff `I001` at `tests/unit/test_revision_change_explanation.py:1:1` and full pytest was `4995 passed, 17 skipped`.
- Owner attempted repair: `postmerge/spec-core@f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb` (`fix(core): normalize revision change import`).
- Exact successor diagnostics were downloaded: `ruff.txt` still contains exactly one `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_revision_change_explanation.py:1:1`; `pytest.txt` is `6 passed in 0.17s`. The first formatting repair therefore did not satisfy Ruff, while behavior-focused tests remain green.
- Core Focused Candidate `34709904332 = FAILURE`. Canonical exact successor `34709904327` was still running, but canonical Ruff had already failed; specification validator, Windows path safety, Linux storage regressions and Local Install were green.
- Focused-harness note: `Generate Ruff remediation diff` requires `git status --porcelain` to be empty, but earlier workflow steps have already created `.focused-evidence/ruff.txt` and `.focused-evidence/pytest.txt`; on the observed run the remediation step itself fails before yielding a remediation diff. This harness defect does not erase the real Ruff `I001`; it only prevents automatic fix-diff capture.
- Current net product/test delta remains bounded to `src/athena/knowledge/revision_change_explanation.py` and `tests/unit/test_revision_change_explanation.py`. Ownership remains Spec/Core; Errors does not parallel-edit the owner-held Core slice.
- Required next owner action: run the exact pinned Ruff fixer on the test import block outside the dirty evidence directory or fix the diagnostic harness to ignore its own evidence files, then commit only the required formatting change; require Core Focused and canonical Quality `SUCCESS` on one unchanged exact worker SHA, followed by integrated Develop canonical `SUCCESS` before `FIXED`.

## UI cross-workflow signal not promoted to an Error ID

UI exact `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6` has Core Focused Candidate `34709115243 = FAILURE`; focused tests complete while Ruff outcome fails/remediation runs, and canonical Quality remains in progress. This is not yet a proven independent UI product root cause. Exact remediation evidence must be consumed and deduplicated against current Core history before assigning a stable Error ID.

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
