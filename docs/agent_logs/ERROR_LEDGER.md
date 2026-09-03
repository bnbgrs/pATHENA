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
- Baseline SHA: `647ea036329280378a7e573aca0df905f48ac3b1`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with current Develop in merge `10996f7d375fadc651d1e6644050cdf9257479a5`; prior Error head `1afe9c2db228a3435797a9157023c072b4574a38` and current Develop were retained as parents.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0004`.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`.
- BLOCKED: none.

## Current scan

- Current Develop `647ea036329280378a7e573aca0df905f48ac3b1` includes the verified Core normal-Hybrid composition, Backend ExternalAccessGateway boundaries, and subsequent knowledge temporal-contradiction integration; no new concrete Develop regression is evidenced in this scan.
- `ERR-0004` original failure is exactly Ruff `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61`, caused by constant-name `setattr(window, "_core_transport_ready", False)`.
- UI correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removed that B010 site using a test-only `_DisconnectedStartupWindow` contract.
- Exact run `33792012599` then exposed Ruff `I001`. UI correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e` changed import formatting but did not satisfy Ruff.
- Completed exact run `33797732276` on `d581a88dfb916f2ffb3e358d16d92d502139ce42` confirms the remaining failure was still exactly `I001` at `tests/unit/test_pathena_startup_experience_2900.py:1:1`; Windows path safety, Linux storage, local-install smoke, validator, mypy and full pytest all passed, with `4492 passed, 3 skipped`.
- Root cause of the persistent I001 was symbol ordering inside the local application import: Ruff expects `UI_REFINEMENT_TASKS_2801_2900` before `PathenaStartupExperience` under its configured import ordering.
- UI correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` performs only that symbol-order change. Current UI head `1ffd2fbc063c1836cdc2dd9504ce297807e5745a` contains this correction and removes temporary focused-validation workflow scaffolding.
- Canonical Quality run `33804193396` on exact current UI head already has specification validator PASS, Ruff PASS, mypy PASS, Windows path safety PASS, Linux storage PASS and local-install smoke PASS. Full pytest is still running, so `ERR-0004` is `FIXED_PENDING_VERIFY`, not yet `FIXED`.
- No independent `ERR-0005` exists; the B010→I001 sequence is one UI harness lint cluster under `ERR-0004`.
- Qt deleted-`QProcess` stderr remains warning-only because no current-lineage failing path was reproduced.

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
- checked_sha: `1ffd2fbc063c1836cdc2dd9504ce297807e5745a`
- severity: P2
- area: Quality / Python lint / Qt startup-readiness test harness
- status: `FIXED_PENDING_VERIFY`
- exact evidence:
  - Canonical Quality `33785726577` on `b76115748aed53e3502a71eef10a41b11f97f8ae`: Ruff-only failure with exact `B010` at startup harness line 61; all other required stages passed.
  - UI B010 correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removes constant-name `setattr` with a test-only disconnected-window type.
  - Run `33792012599` exposed `I001`; correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e` was insufficient.
  - Completed run `33797732276` proved the remaining failure was still exactly `I001` at line 1, while full pytest passed `4492 passed, 3 skipped` and all non-Ruff required stages were green.
  - UI correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` reorders only the imported symbols so `UI_REFINEMENT_TASKS_2801_2900` precedes `PathenaStartupExperience`, matching Ruff ordering.
  - Current exact-head Quality `33804193396` on `1ffd2fbc063c1836cdc2dd9504ce297807e5745a`: validator PASS, Ruff PASS, mypy PASS, Windows path safety PASS, Linux storage PASS, local-install smoke PASS; full pytest still running at last check.
- reproducible path before final correction: `python -m ruff check src tests scripts` reports `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_pathena_startup_experience_2900.py:1:1`.
- primary root cause: after B010 removal, startup harness import symbol ordering remained inconsistent with Ruff/isort ordering; formatting alone did not change symbol order.
- affected files: `tests/unit/test_pathena_startup_experience_2900.py` only for the final lint correction; no production/runtime defect is implicated.
- fix_commit: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; final I001 ordering correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification executed: exact current-head Ruff PASS plus validator/mypy/Windows/Linux-storage/local-install PASS in canonical run `33804193396`; full pytest pending.
- remaining risks: do not mark FIXED until run `33804193396` completes with pytest and canonical enforcement PASS.
- integrator handoff: keep UI integration pending until exact-head run `33804193396` fully succeeds. If it succeeds, mark `ERR-0004` FIXED and UI-GAP-0004 may be reconsidered for integration.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
