# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only failures reproduced or evidenced on the stated SHA are opened.
- Historical failures are not carried forward unless their signature recurs on the current baseline.
- Cascades are deduplicated under their primary root cause.
- `FIXED` requires observed verification; unverified fixes remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `aed609ef8a7ff4af48e15e3dba953daf35d56b5c`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with current Develop in merge `a9d8383c5135e78eb116129150c614c327075678`; prior Error head `f9e226e21603dc1a745e14151dc382eece45fec3` and current Develop were retained as parents.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0004`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`.
- BLOCKED: none.

## Current scan

- Current Develop `aed609ef8a7ff4af48e15e3dba953daf35d56b5c` is an Integrator documentation commit; no new Develop product/test defect is evidenced by that commit itself.
- `ERR-0004` original canonical failure is now exactly diagnosed from the UI worker's uploaded diagnostics as Ruff `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61`: constant-name `setattr(window, "_core_transport_ready", False)`.
- UI correction commit `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removes that exact `setattr` and replaces the harness object with `_DisconnectedStartupWindow`, preserving the disconnected startup state without changing product code or weakening lint/tests.
- Final UI head `25addc9833d0d655efa46cd48974e160a7f275dd` has canonical Quality run `33792012599`. On the currently observed exact-head run: Linux storage PASS, local-install smoke PASS, Windows path safety PASS; specification validator PASS; Ruff FAIL again; mypy/pytest were still running at scan time. Because Ruff failed again after the B010 correction, `ERR-0004` remains `IN_PROGRESS`. The current post-fix Ruff signature must be taken from the new diagnostics artifact before deciding whether it is a recurrence of B010 or a distinct harness-lint signature. No `ERR-0005` is allocated without that deduplication evidence.
- Qt deleted-`QProcess` stderr remains warning-only because no current-lineage failing path was reproduced.
- Backend owns ExternalAccessGateway runtime-boundary hardening; Core owns normal-Hybrid Search composition; UI still owns the active startup harness correction. Error does not create a competing mutation while the exact UI run is active.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence: product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` integrated; canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke.
- reproducible path before fix: malformed entity/runtime integer boundaries could cross validation before SQL because Python `bool` is an `int` subclass and annotations did not enforce runtime types.
- primary root cause: deletion-ledger APIs lacked explicit bool-safe fail-before-SQL runtime validation.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: 22 focused boundary tests PASS inside canonical Backend run `33749788522`; validator/Ruff/mypy/Windows/Linux-storage/local-install PASS.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: no action required.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- exact evidence: canonical Ruff failure in `33744816398`, import-format-only correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`, canonical Ruff PASS in `33749788522`.
- reproducible path: canonical Ruff on the previous Backend lineage reproduced I001.
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- affected files: `tests/unit/test_deletion_ledger_boundaries.py` only.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Ruff PASS in run `33749788522`.
- remaining risks: none for this signature.
- integrator handoff: no action required.

### ERR-0003 — Shell tests retain obsolete permanently-visible inspector contract

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `f76911dfef6530041d62fb6c2e0ddec242d64231`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED`
- exact evidence: canonical Backend Quality run `33755878184` failed only at full pytest with stale persistent-inspector assertions; fix commit `6253577227d427c9bb00707c3e3e578a16c0f9d6` restored the verified contextual-inspector harness contract; exact affected product/test blobs match UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, whose canonical Quality run `33745885426` succeeded.
- reproducible path before fix: construct `PathenaMainWindow` on Workspace without grounded context; `_sync_inspector_visibility()` correctly hides inspector; obsolete tests asserted permanent visibility.
- primary root cause: test-harness/contract drift after UI-GAP-0002 changed the inspector to contextual visibility.
- affected files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_commit: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification executed: canonical Quality run `33745885426` PASS on byte-identical affected product and focused harness blobs.
- remaining risks: Qt deleted-`QProcess` stderr remains scan-only until reproducible failure evidence appears.
- integrator handoff: already integrated into Develop; preserve contextual-inspector behavior.

### ERR-0004 — UI startup/readiness harness fails canonical Ruff

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `25addc9833d0d655efa46cd48974e160a7f275dd`
- severity: P2
- area: Quality / Python lint / Qt startup-readiness test harness
- status: `IN_PROGRESS`
- exact evidence:
  - Canonical Quality run `33785726577` on `b76115748aed53e3502a71eef10a41b11f97f8ae` failed only at Ruff while Windows path safety, Linux storage, local-install smoke, specification validator, mypy and full pytest passed.
  - UI's uploaded diagnostics identify exact original rule `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61` for constant-name `setattr(window, "_core_transport_ready", False)`.
  - UI fix `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removes that exact call with a test-only `_DisconnectedStartupWindow` subclass.
  - Canonical Quality run `33792012599` on final UI head `25addc9833d0d655efa46cd48974e160a7f275dd` again reports Ruff FAIL. At observation time specification validator PASS, Linux storage PASS, local-install smoke PASS, Windows path safety PASS; remaining Python quality stages had not all completed.
- reproducible path: canonical Ruff on the exact UI final head `25addc9833d0d655efa46cd48974e160a7f275dd` reproduces a post-fix failure.
- primary root cause: original `B010` root cause is verified and corrected by `77e7b4c7...`; current post-fix Ruff root cause is not yet classified because the new diagnostics artifact is not yet available. Do not assume it is the same rule.
- affected files: currently constrained to the UI candidate/test lineage; `tests/unit/test_pathena_startup_experience_2900.py` is the only Python file changed between the previous failing UI SHA and the new final UI SHA. No production/runtime defect is currently implicated.
- fix_commit: original B010 correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; verification incomplete because final exact-head Ruff remains red.
- verification executed: prior full Quality diagnosis; exact-head run `33792012599` currently confirms Ruff still FAIL with platform/storage/install/validator checks already green.
- remaining risks: current Ruff rule text must be read from the new diagnostics artifact after upload; deduplicate before allocating a new ERR-ID. UI owns this active test file while its exact-head run is active.
- integrator handoff: keep UI-GAP-0004 rejected. Consume `33792012599` to completion, read the exact new Ruff diagnostic, apply the smallest harness correction without weakening Ruff/assertions, then require exact-head Ruff plus focused startup/offline verification before integration.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
